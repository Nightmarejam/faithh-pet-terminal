# UDM SSH Discovery — 2026-04-02

## Topology reference

- Gen8 LAN: `servicebox.taileb8c60.ts.net` (`eno2`) per `network_baseline_2026-04-02.md` and live Gen8 `ss` output.
- `~/.ssh/config` previously assumed UDM at `192.168.1.1` — **not on same segment** as Gen8 LAN.

## SSH probes (from WSL)

| Target | Result |
|--------|--------|
| `192.168.1.1` | Connection timed out |
| `192.168.0.1` | Connection timed out |
| `10.0.0.1` | Connection timed out |
| `172.16.0.1` | Connection timed out |
| **`192.168.1.1`** | SSH **reachable** — server offered host key; authentication **`Permission denied (publickey,keyboard-interactive)`** for `root` |

## nmap

- `nmap -sn 192.168.1.0/24` from WSL: **0 hosts up** (WSL typically does not bridge to home LAN for that subnet).

## Conclusion

- **Likely gateway / UniFi appliance:** `192.168.1.1` (same /24 as Gen8).
- **SSH:** **Reachable (yes)** — TCP/22 responds; **Authenticated access (no)** without UniFi-configured SSH key or password for `root`.
- **Next step:** In UniFi: **Settings → System → Device SSH** — enable SSH, set credentials/keys, then add `Host udm` in `~/.ssh/config` with `HostName 192.168.1.1` and the correct user/key.
