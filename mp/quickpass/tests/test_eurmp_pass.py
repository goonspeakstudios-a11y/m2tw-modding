#!/usr/bin/env python3
"""Loopback tests for eurmp_pass.py: two or three "PCs" on 127.0.0.1 in temp folders.

Run:
    python mp/quickpass/tests/test_eurmp_pass.py
"""

from __future__ import annotations

import json
import os
import socket
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import eurmp_pass as ep  # noqa: E402

SECRET = b"test-secret-phrase-123"


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Rig:
    """One simulated player: config, saves folder, receiver, watcher."""

    def __init__(self, root: Path, me: str, players: list[dict], secret: bytes = SECRET):
        self.dir = root / me
        (self.dir / "saves").mkdir(parents=True)
        port = next(p["port"] for p in players if p["name"] == me)
        cfg_path = self.dir / "config.json"
        cfg_path.write_text(json.dumps({
            "me": me,
            "port": port,
            "saves_dir": str(self.dir / "saves"),
            "save_glob": "*MP*.sav",
            "stable_seconds": 0.2,
            "players": players,
        }), encoding="utf-8")
        self.cfg = ep.load_config(cfg_path, secret_override=secret)
        self.state = ep.State(self.cfg.state_path)
        self.received: list[str] = []
        self.server = ep.Receiver(self.cfg, self.state, lambda p, s: self.received.append(p.name))
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.stop = threading.Event()
        self.watcher = ep.Watcher(self.cfg, self.state, self.stop)

    def saves(self) -> Path:
        return self.cfg.saves_dir

    def close(self) -> None:
        self.stop.set()
        self.server.shutdown()
        self.server.server_close()


def wait_for(pred, timeout=10.0) -> bool:
    end = time.time() + timeout
    while time.time() < end:
        if pred():
            return True
        time.sleep(0.05)
    return False


class QuickPassTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.players = [
            {"name": "a", "host": "127.0.0.1", "port": free_port()},
            {"name": "b", "host": "127.0.0.1", "port": free_port()},
            {"name": "c", "host": "127.0.0.1", "port": free_port()},
        ]
        self.rigs = {n: Rig(self.root, n, self.players) for n in "abc"}
        ep.SEND_BACKOFF_S = (0, 0, 0, 0)

    def tearDown(self):
        for r in self.rigs.values():
            r.close()
        self.tmp.cleanup()

    def test_send_arrives_intact(self):
        a, b = self.rigs["a"], self.rigs["b"]
        data = os.urandom(3 * 1024 * 1024 + 17)
        src = a.saves() / "EUR_MP turn 1.sav"
        src.write_bytes(data)
        ep.send_file(a.cfg, src, a.cfg.next_peer())
        dst = b.saves() / "EUR_MP turn 1.sav"
        self.assertEqual(dst.read_bytes(), data)
        self.assertEqual(b.received, ["EUR_MP turn 1.sav"])
        self.assertEqual(b.state.get(dst.name), ep.sha256_file(dst))

    def test_ring_wraps(self):
        self.assertEqual(self.rigs["a"].cfg.next_peer().name, "b")
        self.assertEqual(self.rigs["c"].cfg.next_peer().name, "a")

    def test_overwrite_keeps_backup(self):
        a, b = self.rigs["a"], self.rigs["b"]
        (b.saves() / "x MP.sav").write_bytes(b"old")
        src = a.saves() / "x MP.sav"
        src.write_bytes(b"new")
        ep.send_file(a.cfg, src, a.cfg.peer("b"))
        self.assertEqual((b.saves() / "x MP.sav").read_bytes(), b"new")
        backups = list(b.saves().glob("x MP.bak_*.sav"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), b"old")

    def test_wrong_secret_refused(self):
        a, b = self.rigs["a"], self.rigs["b"]
        a.cfg.secret = b"some-other-secret-value"
        src = a.saves() / "MP.sav"
        src.write_bytes(b"data")
        with self.assertRaises(ep.TransferError) as cm:
            ep.send_file(a.cfg, src, a.cfg.peer("b"))
        self.assertIn("bad signature", str(cm.exception))
        self.assertFalse((b.saves() / "MP.sav").exists())

    def test_wrong_recipient_refused(self):
        a = self.rigs["a"]
        src = a.saves() / "MP.sav"
        src.write_bytes(b"data")
        wrong = ep.Peer("c", "127.0.0.1", a.cfg.peer("b").port)
        with self.assertRaises(ep.TransferError) as cm:
            ep.send_file(a.cfg, src, wrong)
        self.assertIn("addressed to c", str(cm.exception))

    def test_replay_refused(self):
        a, b = self.rigs["a"], self.rigs["b"]
        header = {"v": 1, "from": "a", "to": "b", "name": "MP.sav", "size": 4,
                  "sha256": ep.hashlib.sha256(b"data").hexdigest(),
                  "ts": int(time.time()), "nonce": "n" * 32}
        header["mac"] = ep.sign(header, SECRET)
        replies = []
        for _ in range(2):
            with socket.create_connection(("127.0.0.1", b.cfg.port)) as s:
                s.sendall(json.dumps(header).encode() + b"\n" + b"data")
                replies.append(s.makefile("rb").readline().decode().strip())
        self.assertEqual(replies[0], "OK")
        self.assertTrue(replies[1].startswith("ERR replayed"))

    def test_path_traversal_refused(self):
        b = self.rigs["b"]
        header = {"v": 1, "from": "a", "to": "b", "name": "../evil.sav", "size": 4,
                  "sha256": ep.hashlib.sha256(b"data").hexdigest(),
                  "ts": int(time.time()), "nonce": "m" * 32}
        header["mac"] = ep.sign(header, SECRET)
        with socket.create_connection(("127.0.0.1", b.cfg.port)) as s:
            s.sendall(json.dumps(header).encode() + b"\n" + b"data")
            reply = s.makefile("rb").readline().decode().strip()
        self.assertEqual(reply, "ERR bad file name")
        self.assertFalse((b.dir / "evil.sav").exists())

    def test_watcher_passes_new_save_and_does_not_echo(self):
        a, b, c = self.rigs["a"], self.rigs["b"], self.rigs["c"]
        (a.saves() / "old MP.sav").write_bytes(b"existing before start")
        for r in (a, b, c):
            threading.Thread(target=r.watcher.run, daemon=True).start()
        time.sleep(0.3)
        (a.saves() / "EUR_MP turn 2.sav").write_bytes(b"turn two")
        (a.saves() / "not a match.sav").write_bytes(b"ignored")
        self.assertTrue(wait_for(lambda: (b.saves() / "EUR_MP turn 2.sav").exists()))
        # b received it but must not pass it on to c until b saves a new version.
        time.sleep(1.5)
        self.assertFalse((c.saves() / "EUR_MP turn 2.sav").exists())
        self.assertFalse((b.saves() / "old MP.sav").exists())
        self.assertFalse((b.saves() / "not a match.sav").exists())
        # b plays and saves over the same file: now it goes to c.
        (b.saves() / "EUR_MP turn 2.sav").write_bytes(b"turn two, b played")
        self.assertTrue(wait_for(
            lambda: (c.saves() / "EUR_MP turn 2.sav").exists()
            and (c.saves() / "EUR_MP turn 2.sav").read_bytes() == b"turn two, b played"))

    def test_config_errors(self):
        bad = self.root / "bad.json"
        bad.write_text(json.dumps({"me": "z", "saves_dir": str(self.root), "players": self.players}))
        with self.assertRaises(ep.ConfigError):
            ep.load_config(bad, secret_override=SECRET)
        os.environ.pop("EURMP_SECRET", None)
        good = self.rigs["a"].dir / "config.json"
        with self.assertRaises(ep.ConfigError):
            ep.load_config(good)


if __name__ == "__main__":
    unittest.main(verbosity=2)
