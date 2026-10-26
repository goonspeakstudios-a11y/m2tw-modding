# EUR quick-pass: online hotseat while the full MP mod is built

`eurmp_pass.py` sends a hotseat save straight to the next player's PC and opens the game
there. Stdlib-only Python 3.10+, one file, no server.

## One-time setup (every player)

1. Install Python 3.10+ from python.org (tick "Add to PATH" / the `py` launcher).
2. Join the same virtual LAN: Tailscale, ZeroTier or Radmin VPN. Note each player's
   virtual-LAN IP address.
3. Copy this folder anywhere. Copy `config.example.json` to `config.json` and set:
   - `me`: your name, exactly as in `players`.
   - `saves_dir`: your EUR saves folder (where the game writes `.sav` files when you save
     inside the mod; check by saving once and looking for the file).
   - `launch`, `launch_cwd`, `process_name`: how to start the game on your PC (the M2EX
     executable or the shortcut target you normally use, split into a list if it has
     arguments). Leave `launch` as `[]` to only get a beep.
   - `players`: everyone, in turn order, with their virtual-LAN IP. Every player uses the
     same list and order.
4. Edit `start_quickpass.bat` and replace `change-this-to-your-group-phrase` with a phrase
   the whole group shares (12+ characters). The script refuses the placeholder.
5. Allow Python through Windows Firewall on port 47815 (Windows asks on the first run;
   choose Private networks, which covers the virtual LAN adapter).
6. Run `py -3 eurmp_pass.py check --config config.json` and confirm every player shows
   "reachable".

## Playing

- Start a hotseat campaign once (the first player), with each human on their own faction.
- Everyone double-clicks `start_quickpass.bat` and leaves it open.
- On your turn: play, end your turn up to the next human's faction, save with **MP** in the
  name (for example `EUR_MP turn 12.sav`), quit to menu or desktop.
- Within a few seconds the save is on the next player's PC, their game opens, and the
  window shows "Your turn". They load the newest MP save and play.
- Saving over the same file name each turn is fine; the receiver keeps every overwritten
  version as `<name>.bak_<date-time>.sav`.

Manual resend (e.g. the next player was offline):

```
py -3 eurmp_pass.py send "<saves folder>\EUR_MP turn 12.sav" --config config.json
py -3 eurmp_pass.py send "<file>" --to player3 --config config.json
```

## Behaviour

| Situation | What happens |
|---|---|
| New or changed MP save, stopped changing for `stable_seconds` | Sent to the next player in `players`, the ring wraps to the first |
| Save received from another player | Written atomically, game started if not running, never passed on until you save it again |
| MP saves already present when the script starts | Treated as already handled, not sent |
| Next player offline | 5 attempts with 2/4/8/16 s backoff, then an error; resend with `send` |
| Shared secret differs | Receiver answers "bad signature", nothing written |
| PC clocks more than 10 minutes apart | Refused as stale; turn on automatic time sync |
| Same transfer sent twice (replay) | Refused |
| File name with a path or not ending `.sav` | Refused |
| Truncated or corrupted transfer | SHA-256 mismatch, partial file deleted, sender gets an error |
| Game already running on receipt | Not started again (Windows, by `process_name`) |
| Ctrl+C or closing the window | Listener and watcher stop cleanly |

## Limits

- Turns are sequential, as in normal hotseat. Battles between humans are autoresolved or
  fought by the player whose turn it is.
- The game opens at the main menu; loading the save is one click in the load menu. Loading
  it automatically needs an M2EX hook (planned for the full MP mod).
- Hotseat factions are protected only by the game's own hotseat passwords, if you use them.

## Tests

```
python mp/quickpass/tests/test_eurmp_pass.py
```

Loopback tests with three simulated players: intact transfer, ring order, backup on
overwrite, wrong secret, wrong recipient, replay, path traversal, watcher passes new saves
and never echoes received ones, config errors.
