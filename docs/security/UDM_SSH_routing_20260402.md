# UDM SSH routing — 2026-04-02

## Why SSH “hung” from WSL

WSL2 uses a **virtual Ethernet** to Windows, not your LAN NIC.

| Context | Default gateway | Meaning |
|---------|-----------------|--------|
| **WSL** | `172.24.192.1` via `eth0` | Windows vEthernet (WSL). Not your UniFi LAN. |
| **Gen8** (`servicebox`) | `192.158.1.1` via `eno2` | **Actual LAN default gateway = UDM** |

So from WSL, targets like `192.168.1.1` or `192.158.1.243` often **do not route** (or behave oddly) because WSL is not on `192.158.0.0/16`. **Workarounds:** SSH port-forwarding or a jump host on Windows, **Tailscale** to the Gen8 node, or run clients from a host that shares the LAN. Service docs in this repo standardize on Gen8 LAN **`192.158.1.243`** for ChromaDB, SSH, and metrics. On Gen8 itself, the UDM is reachable at `192.158.1.1`.

## Discovery results (this session)

### WSL

```text
default via 172.24.192.1 dev eth0
inet 172.24.202.171/20 dev eth0
```

- `traceroute` / `tracepath`: not installed → skipped.
- Scan `172.24.192.{1,254}` for SSH: **timeouts** (expected — not UDM).

### Gen8

```text
default via 192.158.1.1 dev eno2 proto dhcp src 192.158.1.243
```

| Target | Ping from Gen8 |
|--------|----------------|
| `10.1.89.1` | 100% loss |
| `192.168.1.1` | 100% loss |
| **`192.158.1.1`** | **OK** |

| Target | SSH from Gen8 as `root` |
|--------|-------------------------|
| `192.158.1.1` | TCP/SSH reaches host; **auth** depends on keys on UDM |

### WSL → UDM via jump

```bash
ssh -J gen8 root@192.158.1.1
```

- **Routing:** succeeds quickly (no hang).
- **Auth:** `Permission denied (publickey,...)` with `id_ed25519` and `servicebox_ed25519` from this environment — fix **`~/.ssh/authorized_keys` on UDM for `root`** to include the public key you intend to use from WSL, or set `IdentityFile` in `~/.ssh/config` to that key.

## SSH config change

`~/.ssh/config` — `Host unifi udm dream-machine`:

- `HostName 192.158.1.1` (was `192.168.1.1`)
- `ProxyJump gen8`
- `IdentityFile ~/.ssh/id_ed25519` + `IdentitiesOnly yes` (adjust if your UDM key differs)

Test:

```bash
ssh udm "uname -a"
```

## Note on `10.1.89.1`

That address is **not** the Gen8-reachable gateway on this network. Do not use it as `HostName` unless you have a separate routed path (e.g. another VLAN/site).
