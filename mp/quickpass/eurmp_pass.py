#!/usr/bin/env python3
"""EUR quick-pass - hand a hotseat save to the next player's PC and open the game there.

Stopgap for online EUR campaigns until the full MP mod exists. Every player runs this
script in `run` mode next to their game. It does two things at once:

  * listens on a TCP port for a save sent by another player, checks it, writes it into
    the local saves folder (backing up any older file of the same name), beeps, and
    starts the game if it is not already running;
  * watches the local saves folder; when a save whose name matches `save_glob` is
    written and has stopped changing, it sends it to the next player in `players`
    (the ring wraps from the last player to the first).

So a turn is: play your faction, save as e.g. "EUR_MP turn 12.sav", quit. The script ships
it to the next player, whose game opens; they load the newest MP save and play.

Players must be able to reach each other's port: same LAN, or a virtual LAN such as
Tailscale, ZeroTier or Radmin VPN (use the virtual-LAN IP addresses in `players`).
Every transfer is signed with a shared secret (HMAC-SHA256) read from the environment
variable named in `secret_env`, checked for size and SHA-256, and rejected if stale or
replayed. A save received from another player is never sent on again unless it is
changed (that is, saved again) on this PC.

Stdlib-only Python 3.10+. Windows is the target; also runs on Linux for testing.

Run:
    set EURMP_SECRET=some-long-shared-phrase
    python eurmp_pass.py run --config config.json
    python eurmp_pass.py send "<saves folder>/EUR_MP turn 12.sav" --config config.json
    python eurmp_pass.py send "<file>" --to alice --config config.json
    python eurmp_pass.py check --config config.json

Exit codes: 0 = ok, 1 = transfer failed or peers unreachable (check), 2 = bad config or
arguments.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import hmac
import json
import logging
import os
import secrets
import signal
import socket
import socketserver
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

PROTOCOL_VERSION = 1
DEFAULT_PORT = 47815
MAX_SAVE_BYTES = 512 * 1024 * 1024
MAX_HEADER_BYTES = 8192
MAX_CLOCK_SKEW_S = 600
CHUNK = 1024 * 1024
SEND_ATTEMPTS = 5
SEND_BACKOFF_S = (2, 4, 8, 16)
CONNECT_TIMEOUT_S = 10
IO_TIMEOUT_S = 120
POLL_INTERVAL_S = 2.0
STATE_FILE = "eurmp_pass_state.json"

log = logging.getLogger("eurmp_pass")


class ConfigError(Exception):
    pass


class TransferError(Exception):
    pass


@dataclass
class Peer:
    name: str
    host: str
    port: int


@dataclass
class Config:
    me: str
    secret: bytes
    port: int
    saves_dir: Path
    save_glob: str
    stable_seconds: float
    players: list[Peer]
    launch: list[str] = field(default_factory=list)
    launch_cwd: Path | None = None
    process_name: str = ""
    state_path: Path = Path(STATE_FILE)

    def peer(self, name: str) -> Peer:
        for p in self.players:
            if p.name == name:
                return p
        raise ConfigError(f"no player named {name!r} in players")

    def next_peer(self) -> Peer:
        names = [p.name for p in self.players]
        i = names.index(self.me)
        return self.players[(i + 1) % len(self.players)]


def load_config(path: Path, secret_override: bytes | None = None) -> Config:
    try:
        raw = json.loads(path.read_text(encoding="utf-8-sig"))
    except OSError as e:
        raise ConfigError(f"cannot read config {path}: {e}") from e
    except json.JSONDecodeError as e:
        raise ConfigError(f"config {path} is not valid JSON: {e}") from e

    def need(key: str):
        if key not in raw:
            raise ConfigError(f"config is missing {key!r}")
        return raw[key]

    me = str(need("me"))
    secret_env = str(raw.get("secret_env", "EURMP_SECRET"))
    if secret_override is not None:
        secret = secret_override
    else:
        value = os.environ.get(secret_env, "")
        if len(value) < 12 or value == "change-this-to-your-group-phrase":
            raise ConfigError(
                f"environment variable {secret_env} must hold the shared secret (12+ characters)"
            )
        secret = value.encode("utf-8")

    players = []
    seen = set()
    for entry in need("players"):
        name = str(entry["name"])
        if name in seen:
            raise ConfigError(f"player {name!r} listed twice")
        seen.add(name)
        players.append(Peer(name, str(entry["host"]), int(entry.get("port", DEFAULT_PORT))))
    if len(players) < 2:
        raise ConfigError("players needs at least two entries")
    if me not in seen:
        raise ConfigError(f"me={me!r} is not in players")

    saves_dir = Path(need("saves_dir")).expanduser()
    if not saves_dir.is_dir():
        raise ConfigError(f"saves_dir {saves_dir} does not exist")

    launch = raw.get("launch") or []
    if isinstance(launch, str):
        launch = [launch]
    launch_cwd = raw.get("launch_cwd")
    state = raw.get("state_file")
    return Config(
        me=me,
        secret=secret,
        port=int(raw.get("port", DEFAULT_PORT)),
        saves_dir=saves_dir,
        save_glob=str(raw.get("save_glob", "*MP*.sav")),
        stable_seconds=float(raw.get("stable_seconds", 3)),
        players=players,
        launch=[str(x) for x in launch],
        launch_cwd=Path(launch_cwd) if launch_cwd else None,
        process_name=str(raw.get("process_name", "")),
        state_path=Path(state) if state else path.with_name(STATE_FILE),
    )


# ---------------------------------------------------------------- state


class State:
    """Name -> SHA-256 of the last version of each save sent or received here."""

    def __init__(self, path: Path):
        self.path = path
        self.lock = threading.Lock()
        self.known: dict[str, str] = {}
        try:
            self.known = dict(json.loads(path.read_text(encoding="utf-8")).get("known", {}))
        except FileNotFoundError:
            pass
        except (OSError, json.JSONDecodeError, AttributeError) as e:
            log.warning("state file %s unreadable (%s); starting fresh", path, e)

    def get(self, name: str) -> str | None:
        with self.lock:
            return self.known.get(name)

    def set(self, name: str, digest: str) -> None:
        with self.lock:
            self.known[name] = digest
            tmp = self.path.with_suffix(".tmp")
            try:
                tmp.write_text(json.dumps({"known": self.known}, indent=1), encoding="utf-8")
                os.replace(tmp, self.path)
            except OSError as e:
                log.error("cannot write state file %s: %s", self.path, e)


# ---------------------------------------------------------------- protocol


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(CHUNK), b""):
            h.update(block)
    return h.hexdigest()


def _mac_fields(header: dict) -> bytes:
    keys = ("v", "from", "to", "name", "size", "sha256", "ts", "nonce")
    return json.dumps([header[k] for k in keys], separators=(",", ":")).encode("utf-8")


def sign(header: dict, secret: bytes) -> str:
    return hmac.new(secret, _mac_fields(header), hashlib.sha256).hexdigest()


def valid_save_name(name: str) -> bool:
    return (
        bool(name)
        and name == os.path.basename(name)
        and "/" not in name
        and "\\" not in name
        and name not in (".", "..")
        and name.lower().endswith(".sav")
        and len(name) <= 200
    )


def send_file(cfg: Config, path: Path, peer: Peer) -> str:
    """Send one save to one peer, retrying with backoff. Returns the file's SHA-256."""
    name = path.name
    if not valid_save_name(name):
        raise TransferError(f"{name!r} is not a .sav file name")
    size = path.stat().st_size
    if size > MAX_SAVE_BYTES:
        raise TransferError(f"{name} is {size} bytes, over the {MAX_SAVE_BYTES} limit")
    digest = sha256_file(path)

    last_error: Exception | None = None
    for attempt in range(1, SEND_ATTEMPTS + 1):
        header = {
            "v": PROTOCOL_VERSION,
            "from": cfg.me,
            "to": peer.name,
            "name": name,
            "size": size,
            "sha256": digest,
            "ts": int(time.time()),
            "nonce": secrets.token_hex(16),
        }
        header["mac"] = sign(header, cfg.secret)
        try:
            with socket.create_connection((peer.host, peer.port), timeout=CONNECT_TIMEOUT_S) as s:
                s.settimeout(IO_TIMEOUT_S)
                s.sendall(json.dumps(header).encode("utf-8") + b"\n")
                with path.open("rb") as f:
                    sent = 0
                    while sent < size:
                        block = f.read(min(CHUNK, size - sent))
                        if not block:
                            raise TransferError(f"{name} shrank while being sent")
                        s.sendall(block)
                        sent += len(block)
                reply = s.makefile("rb").readline(512).decode("utf-8", "replace").strip()
            if reply == "OK":
                log.info("sent %s (%d bytes) to %s", name, size, peer.name)
                return digest
            if reply.startswith("ERR"):
                # The receiver refused the file; retrying the same bytes will not help.
                raise TransferError(f"{peer.name} refused {name}: {reply[4:] or 'no reason'}")
            last_error = TransferError(f"unexpected reply from {peer.name}: {reply!r}")
        except TransferError:
            raise
        except OSError as e:
            last_error = e
        if attempt < SEND_ATTEMPTS:
            wait = SEND_BACKOFF_S[min(attempt - 1, len(SEND_BACKOFF_S) - 1)]
            log.warning(
                "send %s to %s failed (%s); retry %d/%d in %ds",
                name, peer.name, last_error, attempt, SEND_ATTEMPTS - 1, wait,
            )
            time.sleep(wait)
    raise TransferError(f"could not send {name} to {peer.name}: {last_error}")


# ---------------------------------------------------------------- receiving


class Receiver(socketserver.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, cfg: Config, state: State, on_received=None):
        self.cfg = cfg
        self.state = state
        self.on_received = on_received
        self.nonces: dict[str, float] = {}
        self.nonce_lock = threading.Lock()
        self.write_lock = threading.Lock()
        super().__init__(("0.0.0.0", cfg.port), ReceiveHandler)

    def fresh_nonce(self, nonce: str) -> bool:
        now = time.time()
        with self.nonce_lock:
            for n, t in list(self.nonces.items()):
                if now - t > 2 * MAX_CLOCK_SKEW_S:
                    del self.nonces[n]
            if nonce in self.nonces:
                return False
            self.nonces[nonce] = now
            return True


class ReceiveHandler(socketserver.StreamRequestHandler):
    server: Receiver

    def reply(self, text: str) -> None:
        try:
            self.wfile.write(text.encode("utf-8") + b"\n")
            self.wfile.flush()
        except OSError:
            pass

    def handle(self) -> None:
        peer_addr = self.client_address[0]
        self.request.settimeout(IO_TIMEOUT_S)
        try:
            line = self.rfile.readline(MAX_HEADER_BYTES)
            header = json.loads(line)
            if not isinstance(header, dict):
                raise ValueError("header is not an object")
        except (OSError, ValueError) as e:
            log.warning("bad header from %s: %s", peer_addr, e)
            self.reply("ERR bad header")
            return

        cfg = self.server.cfg
        err = self.check_header(header)
        if err:
            log.warning("rejected transfer from %s: %s", peer_addr, err)
            self.reply(f"ERR {err}")
            return

        name, size, digest = header["name"], header["size"], header["sha256"]
        tmp = cfg.saves_dir / f".{name}.{header['nonce'][:8]}.part"
        h = hashlib.sha256()
        try:
            with tmp.open("wb") as f:
                left = size
                while left:
                    block = self.rfile.read(min(CHUNK, left))
                    if not block:
                        raise TransferError("connection closed mid-file")
                    h.update(block)
                    f.write(block)
                    left -= len(block)
            if h.hexdigest() != digest:
                raise TransferError("SHA-256 mismatch")
            target = cfg.saves_dir / name
            with self.server.write_lock:
                if target.exists():
                    if sha256_file(target) == digest:
                        tmp.unlink()
                        self.server.state.set(name, digest)
                        self.reply("OK")
                        log.info("%s from %s already present", name, header["from"])
                        return
                    backup = target.with_name(f"{target.stem}.bak_{time.strftime('%Y%m%d-%H%M%S')}.sav")
                    os.replace(target, backup)
                    log.info("kept the older %s as %s", name, backup.name)
                # Record before the rename so the watcher never sees an unknown version.
                self.server.state.set(name, digest)
                os.replace(tmp, target)
        except (OSError, TransferError) as e:
            log.error("receiving %s from %s failed: %s", name, header.get("from"), e)
            try:
                tmp.unlink()
            except OSError:
                pass
            self.reply(f"ERR {e}")
            return

        self.reply("OK")
        log.info("received %s (%d bytes) from %s", name, size, header["from"])
        if self.server.on_received:
            try:
                self.server.on_received(cfg.saves_dir / name, header["from"])
            except Exception:
                log.exception("post-receive action failed")

    def check_header(self, h: dict) -> str | None:
        cfg = self.server.cfg
        needed = ("v", "from", "to", "name", "size", "sha256", "ts", "nonce", "mac")
        if any(k not in h for k in needed):
            return "incomplete header"
        if h["v"] != PROTOCOL_VERSION:
            return f"protocol version {h['v']} not supported"
        if not hmac.compare_digest(str(h["mac"]), sign(h, cfg.secret)):
            return "bad signature (shared secret differs?)"
        if h["to"] != cfg.me:
            return f"addressed to {h['to']}, this is {cfg.me}"
        if h["from"] not in {p.name for p in cfg.players}:
            return f"unknown sender {h['from']}"
        if not isinstance(h["ts"], int) or abs(time.time() - h["ts"]) > MAX_CLOCK_SKEW_S:
            return "stale or future timestamp (check both PC clocks)"
        if not self.server.fresh_nonce(str(h["nonce"])):
            return "replayed transfer"
        if not valid_save_name(str(h["name"])):
            return "bad file name"
        if not isinstance(h["size"], int) or not 0 < h["size"] <= MAX_SAVE_BYTES:
            return "bad size"
        return None


# ---------------------------------------------------------------- game launch


def game_running(process_name: str) -> bool:
    if not process_name or os.name != "nt":
        return False
    try:
        out = subprocess.run(
            ["tasklist", "/FI", f"IMAGENAME eq {process_name}", "/NH"],
            capture_output=True, text=True, timeout=10,
        ).stdout
    except (OSError, subprocess.SubprocessError) as e:
        log.warning("cannot check whether %s is running: %s", process_name, e)
        return False
    return process_name.lower() in out.lower()


def notify(text: str) -> None:
    print(f"\n*** {text} ***\n", flush=True)
    if os.name == "nt":
        try:
            import winsound
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except (ImportError, RuntimeError):
            pass


def make_on_received(cfg: Config):
    def on_received(path: Path, sender: str) -> None:
        notify(f"Your turn: {path.name} arrived from {sender}. Load it from the saves menu.")
        if not cfg.launch:
            return
        if game_running(cfg.process_name):
            log.info("game already running; not starting another copy")
            return
        try:
            flags = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            subprocess.Popen(cfg.launch, cwd=str(cfg.launch_cwd) if cfg.launch_cwd else None, creationflags=flags)
            log.info("started the game: %s", " ".join(cfg.launch))
        except OSError as e:
            log.error("could not start the game (%s): %s", cfg.launch, e)
    return on_received


# ---------------------------------------------------------------- watching


class Watcher:
    """Send matching saves to the next player once they stop changing."""

    def __init__(self, cfg: Config, state: State, stop: threading.Event):
        self.cfg = cfg
        self.state = state
        self.stop = stop
        self.seen: dict[str, tuple[int, int, float]] = {}

    def matching(self) -> list[Path]:
        try:
            return [
                p for p in self.cfg.saves_dir.iterdir()
                if p.is_file()
                and valid_save_name(p.name)
                and ".bak_" not in p.name
                and fnmatch.fnmatch(p.name.lower(), self.cfg.save_glob.lower())
            ]
        except OSError as e:
            log.error("cannot list %s: %s", self.cfg.saves_dir, e)
            return []

    def seed(self) -> None:
        """Treat saves already on disk at start-up as known, so nothing old is re-sent."""
        for p in self.matching():
            if self.state.get(p.name) is None:
                try:
                    self.state.set(p.name, sha256_file(p))
                except OSError as e:
                    log.warning("cannot hash %s: %s", p.name, e)

    def poll_once(self) -> None:
        now = time.time()
        for p in self.matching():
            try:
                st = p.stat()
            except OSError:
                continue
            key = (st.st_size, st.st_mtime_ns)
            prev = self.seen.get(p.name)
            if prev is None or prev[:2] != key:
                self.seen[p.name] = (key[0], key[1], now)
                continue
            if now - prev[2] < self.cfg.stable_seconds:
                continue
            try:
                digest = sha256_file(p)
            except OSError as e:
                log.warning("cannot hash %s: %s", p.name, e)
                continue
            if digest == self.state.get(p.name):
                continue
            peer = self.cfg.next_peer()
            log.info("new save %s; passing it to %s", p.name, peer.name)
            try:
                send_file(self.cfg, p, peer)
                self.state.set(p.name, digest)
                notify(f"{p.name} sent to {peer.name}. Their turn.")
            except (TransferError, OSError) as e:
                log.error("%s; it will be retried on the next change, or use the send command", e)
                # Remember the failed version so the loop does not hammer the peer.
                self.state.set(p.name, digest)

    def run(self) -> None:
        self.seed()
        while not self.stop.is_set():
            self.poll_once()
            self.stop.wait(POLL_INTERVAL_S)


# ---------------------------------------------------------------- commands


def cmd_run(cfg: Config) -> int:
    state = State(cfg.state_path)
    stop = threading.Event()
    try:
        server = Receiver(cfg, state, make_on_received(cfg))
    except OSError as e:
        log.error("cannot listen on port %d: %s", cfg.port, e)
        return 1
    threading.Thread(target=server.serve_forever, name="receiver", daemon=True).start()
    watcher = Watcher(cfg, state, stop)
    watch_thread = threading.Thread(target=watcher.run, name="watcher", daemon=True)
    watch_thread.start()

    def shutdown(*_):
        stop.set()
    signal.signal(signal.SIGINT, shutdown)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, shutdown)
    if hasattr(signal, "SIGBREAK"):
        signal.signal(signal.SIGBREAK, shutdown)

    log.info(
        "%s listening on port %d, watching %s for %s; next player is %s. Ctrl+C to stop.",
        cfg.me, cfg.port, cfg.saves_dir, cfg.save_glob, cfg.next_peer().name,
    )
    while not stop.is_set():
        stop.wait(0.5)
    log.info("stopping")
    server.shutdown()
    server.server_close()
    watch_thread.join(timeout=5)
    return 0


def cmd_send(cfg: Config, file: Path, to: str | None) -> int:
    peer = cfg.peer(to) if to else cfg.next_peer()
    if not file.is_file():
        log.error("%s does not exist", file)
        return 2
    try:
        digest = send_file(cfg, file, peer)
    except (TransferError, OSError) as e:
        log.error("%s", e)
        return 1
    if file.parent.resolve() == cfg.saves_dir.resolve():
        State(cfg.state_path).set(file.name, digest)
    return 0


def cmd_check(cfg: Config) -> int:
    bad = 0
    for p in cfg.players:
        if p.name == cfg.me:
            continue
        try:
            with socket.create_connection((p.host, p.port), timeout=CONNECT_TIMEOUT_S):
                log.info("%-16s %s:%d reachable", p.name, p.host, p.port)
        except OSError as e:
            log.error("%-16s %s:%d NOT reachable: %s", p.name, p.host, p.port, e)
            bad += 1
    return 1 if bad else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Pass EUR hotseat saves between PCs and open the game.")
    ap.add_argument("--config", type=Path, default=Path(__file__).with_name("config.json"))
    ap.add_argument("-v", "--verbose", action="store_true")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("run", help="listen for saves and pass on new ones")
    sp = sub.add_parser("send", help="send one save now")
    sp.add_argument("file", type=Path)
    sp.add_argument("--to", help="player name (default: next player)")
    sub.add_parser("check", help="test that every other player's port is reachable")
    args = ap.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(message)s",
        datefmt="%H:%M:%S",
    )
    try:
        cfg = load_config(args.config)
        if args.cmd == "run":
            return cmd_run(cfg)
        if args.cmd == "send":
            return cmd_send(cfg, args.file, args.to)
        return cmd_check(cfg)
    except ConfigError as e:
        log.error("%s", e)
        return 2


if __name__ == "__main__":
    sys.exit(main())
