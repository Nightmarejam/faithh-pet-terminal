#!/usr/bin/env python3
"""
Live system pulse: disk I/O for / and /mnt/d, Chroma faithh_knowledge_base count,
RAM vs WSL .wslconfig memory limit, and network vitals (DSM ping + NFS staging).

Chroma connection (in order):
  - If CHROMA_PERSIST_PATH is set: chromadb.PersistentClient(path=...) (e.g. D: tier under WSL).
  - Else: CHROMA_HOST / CHROMA_PORT (or legacy CHROMADB_*) → HttpClient.

Also: CHROMA_COLLECTION, CHROMA_MAINT_REQUEST_TIMEOUT_S, RAW_DATA_STAGING (staging path only;
  not read by this script — for operators / other tooling).

Network: PULSE_DSM_HOST (default nas.taileb8c60.ts.net) for ICMP average RTT; /mnt/nas-staging is
  checked for native NFS (nfs/nfs4) to confirm DrvFs bypass.

Examples:
  python3 scripts/system_pulse.py
  python3 scripts/system_pulse.py --interval 0.75
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import time
from pathlib import Path
from urllib.parse import urlparse

try:
    from rich import box
    from rich.console import Console
    from rich.markup import escape
    from rich.panel import Panel
    from rich.table import Table

    _RICH = True
except ImportError:
    _RICH = False
    escape = lambda s: s  # type: ignore[misc, assignment, no-redef]

import psutil

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    chromadb = None  # type: ignore[misc, assignment]
    Settings = None  # type: ignore[misc, assignment]


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DSM_HOST = "nas.taileb8c60.ts.net"
NFS_STAGING_MOUNT = "/mnt/nas-staging"
WSLCONFIG_CANDIDATES = (
    Path("/mnt/c/Users/jonat/.wslconfig"),
    Path.home().parent / ".wslconfig",  # unlikely on WSL; harmless
)


def _load_repo_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    env_path = REPO_ROOT / ".env"
    if env_path.is_file():
        load_dotenv(env_path, override=False)


def _chroma_host_raw() -> str:
    h = (os.environ.get("CHROMA_HOST") or "").strip()
    if h:
        return h
    legacy = (os.environ.get("CHROMADB_HOST") or "").strip()
    if legacy:
        p = os.environ.get("CHROMADB_PORT") or os.environ.get("CHROMA_PORT") or "8000"
        if "://" in legacy:
            return legacy
        return f"http://{legacy}:{p}"
    return "localhost"


def _parse_chroma_host_port() -> tuple[str | None, int | None]:
    """
    If CHROMA_PERSIST_PATH is set, returns (None, None) — caller must use PersistentClient
    with that path. Otherwise returns (host, port) for HttpClient.
    """
    persist = (os.environ.get("CHROMA_PERSIST_PATH") or "").strip()
    if persist:
        return None, None

    raw = _chroma_host_raw()
    if raw.startswith("http://") or raw.startswith("https://"):
        u = urlparse(raw)
        host = u.hostname or "localhost"
        port = int(os.environ.get("CHROMA_PORT", u.port or 8000))
        return host, port
    if ":" in raw and raw.count(":") == 1:
        h, _, p = raw.partition(":")
        return h, int(os.environ.get("CHROMA_PORT", p))
    return raw, int(os.environ.get("CHROMA_PORT", "8000"))


def _chroma_settings() -> "Settings":
    if Settings is None:
        raise RuntimeError("chromadb is not installed")
    timeout_s = int(os.environ.get("CHROMA_MAINT_REQUEST_TIMEOUT_S", "60"))
    return Settings(
        anonymized_telemetry=False,
        chroma_query_request_timeout_seconds=timeout_s,
        chroma_sysdb_request_timeout_seconds=max(timeout_s, 60),
    )


def _get_chroma_client() -> tuple[object, str]:
    """Return (client, display label for dashboard)."""
    if chromadb is None:
        raise RuntimeError("chromadb is not installed")

    settings = _chroma_settings()
    persist = (os.environ.get("CHROMA_PERSIST_PATH") or "").strip()
    if persist:
        client = chromadb.PersistentClient(path=persist, settings=settings)
        return client, f"PersistentClient:{persist}"

    host, port = _parse_chroma_host_port()
    assert host is not None and port is not None
    client = chromadb.HttpClient(host=host, port=port, settings=settings)
    return client, f"{host}:{port}"


def _parse_wsl_memory_gib() -> tuple[float | None, Path | None]:
    """Return configured memory= GiB from .wslconfig if found."""
    for path in WSLCONFIG_CANDIDATES:
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for raw_line in text.splitlines():
            line = raw_line.split("#", 1)[0].strip()
            if not line.lower().startswith("memory="):
                continue
            val = line.split("=", 1)[1].strip().upper().replace(" ", "")
            if val.endswith("GB"):
                try:
                    return float(val[:-2]), path
                except ValueError:
                    return None, path
            if val.endswith("MB"):
                try:
                    return float(val[:-2]) / 1024.0, path
                except ValueError:
                    return None, path
            try:
                return float(val), path
            except ValueError:
                return None, path
    return None, None


def _partition_device(mount: str) -> str | None:
    target = os.path.realpath(mount)
    best: tuple[int, str] | None = None
    for p in psutil.disk_partitions(all=True):
        mp = os.path.realpath(p.mountpoint)
        if target == mp or target.startswith(mp + os.sep):
            depth = len(Path(mp).parts)
            if best is None or depth > best[0]:
                best = (depth, p.device)
    return best[1] if best else None


def _disk_io_stat_key(device: str, available: set[str]) -> str | None:
    base = os.path.basename(device)
    if base in available:
        return base
    if re.match(r"^nvme\d+n\d+p\d+$", base):
        stem = re.sub(r"p\d+$", "", base)
        if stem in available:
            return stem
    if re.match(r"^mmcblk\d+p\d+$", base):
        stem = re.sub(r"p\d+$", "", base)
        if stem in available:
            return stem
    stem = re.sub(r"\d+$", "", base)
    if stem in available:
        return stem
    prefixes = [k for k in available if base.startswith(k) and k != base]
    if prefixes:
        return max(prefixes, key=len)
    return None


def _sample_disk_mb_s(
    mount: str,
    label: str,
    interval: float,
    counters_before: dict,
    counters_after: dict,
) -> tuple[str, float | None, float | None, str | None]:
    dev = _partition_device(mount)
    if not dev:
        return label, None, None, f"no partition for {mount}"
    # WSL DrvFs (e.g. D:\): block I/O is on the Windows host, not in Linux diskstats.
    if len(dev) >= 2 and dev[1] == ":":
        return label, None, None, "DrvFs (I/O on Windows)"
    key = _disk_io_stat_key(dev, set(counters_before.keys()))
    if not key or key not in counters_after:
        return label, None, None, f"no I/O stats for {dev} (key {key!r})"
    b_before = counters_before[key]
    b_after = counters_after[key]
    read_b = max(0, b_after.read_bytes - b_before.read_bytes)
    write_b = max(0, b_after.write_bytes - b_before.write_bytes)
    sec = interval if interval > 0 else 1e-9
    read_mbs = read_b / sec / (1024 * 1024)
    write_mbs = write_b / sec / (1024 * 1024)
    return label, read_mbs, write_mbs, dev


def _fetch_chroma_count(collection: str) -> tuple[int | None, str]:
    try:
        client, label = _get_chroma_client()
        coll = client.get_collection(collection)
        return coll.count(), f"{label} ({collection})"
    except Exception as e:
        return None, str(e)


def _ram_summary() -> tuple[dict, str]:
    vm = psutil.virtual_memory()
    total_gib = vm.total / (1024**3)
    used_gib = vm.used / (1024**3)
    pct = vm.percent
    cfg_gib, cfg_path = _parse_wsl_memory_gib()
    if cfg_gib is not None:
        delta = abs(total_gib - cfg_gib)
        matches = delta <= 1.25 or (delta / cfg_gib) <= 0.06 if cfg_gib else False
        note = (
            f"Guest RAM total ({total_gib:.2f} GiB) matches .wslconfig memory≈{cfg_gib:.0f} GiB: "
            f"{'yes' if matches else 'no — check `wsl --shutdown` then reopen'}"
        )
        if cfg_path:
            note += f"  [{cfg_path}]"
    else:
        note = (
            f"No memory= parsed from .wslconfig (checked {', '.join(str(p) for p in WSLCONFIG_CANDIDATES)}). "
            f"Guest total: {total_gib:.2f} GiB."
        )
    return {
        "total_gib": total_gib,
        "used_gib": used_gib,
        "percent": pct,
        "cfg_gib": cfg_gib,
        "matches_cfg": cfg_gib is not None
        and (
            abs(total_gib - cfg_gib) <= 1.25
            or (abs(total_gib - cfg_gib) / cfg_gib) <= 0.06
        ),
    }, note


def _dsm_host() -> str:
    return (os.environ.get("PULSE_DSM_HOST") or DEFAULT_DSM_HOST).strip() or DEFAULT_DSM_HOST


def _parse_ping_avg_ms(stdout: str) -> float | None:
    """Extract average RTT in ms from ping(8) statistics line."""
    m = re.search(r"min/avg/max(?:/mdev)?\s*=\s*[\d.]+/([\d.]+)/", stdout)
    if not m:
        return None
    try:
        return float(m.group(1))
    except ValueError:
        return None


def _dsm_ping_avg_ms(host: str) -> tuple[float | None, str]:
    """
    Run ping via subprocess; return (average_rtt_ms, detail).
    None average => timeout, failure, or unparseable output.
    """
    try:
        proc = subprocess.run(
            ["ping", "-c", "4", "-W", "2", host],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except subprocess.TimeoutExpired:
        return None, "ping subprocess timed out"
    except OSError as e:
        return None, str(e)

    out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    avg = _parse_ping_avg_ms(out)
    if avg is not None:
        return avg, ""
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "").strip()
        return None, tail[-200:] if tail else f"ping exit {proc.returncode}"
    return None, "no RTT line in ping output"


def _nfs_staging_mounted() -> bool:
    """True if NFS_STAGING_MOUNT is an active mount with fstype nfs or nfs4."""
    mp = Path(NFS_STAGING_MOUNT)
    if not mp.is_dir():
        return False
    try:
        target = mp.resolve()
    except OSError:
        return False
    for p in psutil.disk_partitions(all=True):
        try:
            if Path(p.mountpoint).resolve() != target:
                continue
        except OSError:
            continue
        ft = (p.fstype or "").lower()
        return ft == "nfs" or ft == "nfs4" or ft.startswith("nfs")
    return False


def _network_vital_summary() -> tuple[str, float | None, str, bool]:
    """Returns (host, avg_rtt_ms_or_none, ping_detail_if_error, nfs_staging_ok)."""
    host = _dsm_host()
    avg_ms, err = _dsm_ping_avg_ms(host)
    return host, avg_ms, err, _nfs_staging_mounted()


def _rtt_rich_style(avg_ms: float | None) -> str:
    if avg_ms is None:
        return "red"
    if avg_ms > 20:
        return "red"
    if avg_ms > 5:
        return "yellow"
    return "green"


def _render_rich(
    disk_rows: list[tuple[str, float | None, float | None, str | None]],
    collection: str,
    chroma_count: int | None,
    chroma_meta: str,
    ram: dict,
    ram_note: str,
    net_host: str,
    net_avg_ms: float | None,
    net_err: str,
    nfs_staging: bool,
) -> None:
    console = Console()
    console.print(
        Panel.fit("[bold]FAITHH system pulse[/bold]", border_style="cyan", box=box.DOUBLE)
    )

    io_table = Table(title="Disk I/O (sampled)", box=box.SIMPLE_HEAD)
    io_table.add_column("Mount", style="bold")
    io_table.add_column("Device", max_width=40, overflow="fold")
    io_table.add_column("Read MB/s", justify="right")
    io_table.add_column("Write MB/s", justify="right")
    for label, r, w, dev in disk_rows:
        io_table.add_row(
            label,
            dev or "—",
            f"{r:.2f}" if r is not None else "—",
            f"{w:.2f}" if w is not None else "—",
        )
    console.print(io_table)

    rtt_style = _rtt_rich_style(net_avg_ms)
    if net_avg_ms is not None:
        rtt_line = (
            f"Average RTT: [{rtt_style}]{net_avg_ms:.3f} ms[/{rtt_style}] (DSM {escape(net_host)})"
        )
    else:
        detail = f" — {escape(net_err)}" if net_err else ""
        rtt_line = (
            f"Average RTT: [red]timeout / unreachable[/red]{detail} (DSM {escape(net_host)})"
        )
    nfs_line = (
        f"{NFS_STAGING_MOUNT}: [green]✓ NFS (DrvFs bypass)[/green]"
        if nfs_staging
        else f"{NFS_STAGING_MOUNT}: not mounted as NFS"
    )
    console.print(
        Panel(
            f"{rtt_line}\n{nfs_line}",
            title="Network Vital",
            border_style="cyan",
        )
    )

    ch_text = (
        f"[green]{chroma_count:,}[/green] documents"
        if chroma_count is not None
        else f"[red]unavailable[/red] ({escape(chroma_meta)})"
    )
    console.print(
        Panel(
            f"Collection [bold]{escape(collection)}[/bold]\n{escape(chroma_meta)}\n{ch_text}",
            title="ChromaDB",
            border_style="magenta",
        )
    )

    match_style = "green" if ram.get("matches_cfg") else "yellow"
    console.print(
        Panel(
            f"Used: [bold]{ram['used_gib']:.2f}[/bold] / {ram['total_gib']:.2f} GiB  ({ram['percent']:.1f}%)\n"
            f"[{match_style}]{escape(ram_note)}[/{match_style}]",
            title="Memory",
            border_style="blue",
        )
    )


def _render_ascii(
    disk_rows: list[tuple[str, float | None, float | None, str | None]],
    collection: str,
    chroma_count: int | None,
    chroma_meta: str,
    ram: dict,
    ram_note: str,
    net_host: str,
    net_avg_ms: float | None,
    net_err: str,
    nfs_staging: bool,
) -> None:
    width = 56
    print("+" + "-" * (width - 2) + "+")
    print("|" + " FAITHH system pulse ".center(width - 2) + "|")
    print("+" + "-" * (width - 2) + "+")
    print()
    print("  Disk I/O (MB/s)")
    print("  " + "-" * 42)
    for label, r, w, dev in disk_rows:
        rs = f"{r:.2f}" if r is not None else "  n/a"
        ws = f"{w:.2f}" if w is not None else "  n/a"
        dv = dev or "?"
        print(f"  {label:12}  {dv:10}  read {rs:>8}  write {ws:>8}")
    print()
    print("  Network Vital")
    if net_avg_ms is not None:
        flag = " (!)" if net_avg_ms > 20 else (" (+)" if net_avg_ms > 5 else "")
        print(f"    DSM {net_host}  avg RTT: {net_avg_ms:.3f} ms{flag}")
    else:
        err = f" ({net_err})" if net_err else ""
        print(f"    DSM {net_host}  avg RTT: timeout / unreachable{err}")
    nfs_mark = "✓ NFS (DrvFs bypass)" if nfs_staging else "not mounted as NFS"
    print(f"    {NFS_STAGING_MOUNT}: {nfs_mark}")
    print()
    print(f"  ChromaDB  {collection}")
    if chroma_count is not None:
        print(f"    count: {chroma_count:,}  ({chroma_meta})")
    else:
        print(f"    error: {chroma_meta}")
    print()
    print("  Memory")
    print(f"    used {ram['used_gib']:.2f} / {ram['total_gib']:.2f} GiB  ({ram['percent']:.1f}%)")
    print(f"    {ram_note}")
    print()


def main() -> int:
    ap = argparse.ArgumentParser(
        description="System pulse dashboard (disk I/O, network vital, Chroma, RAM).",
    )
    ap.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Seconds between disk_io_counters samples (default 1.0).",
    )
    ap.add_argument(
        "--collection",
        default=os.environ.get("CHROMA_COLLECTION", "faithh_knowledge_base"),
        help="Chroma collection name (default env CHROMA_COLLECTION or faithh_knowledge_base).",
    )
    ap.add_argument(
        "--no-chroma",
        action="store_true",
        help="Skip Chroma query.",
    )
    args = ap.parse_args()

    _load_repo_dotenv()

    interval = max(0.05, float(args.interval))
    c1 = psutil.disk_io_counters(perdisk=True) or {}
    time.sleep(interval)
    c2 = psutil.disk_io_counters(perdisk=True) or {}

    disk_rows: list[tuple[str, float | None, float | None, str | None]] = []
    for mount, label in (("/", "/ (M.2)"), ("/mnt/d", "/mnt/d/ (external)")):
        if mount == "/mnt/d" and not Path("/mnt/d").is_dir():
            disk_rows.append((label, None, None, "not mounted"))
            continue
        disk_rows.append(_sample_disk_mb_s(mount, label, interval, c1, c2))

    chroma_count: int | None = None
    chroma_meta = ""
    if args.no_chroma:
        chroma_meta = "(skipped)"
    else:
        chroma_count, err_or_host = _fetch_chroma_count(args.collection)
        if chroma_count is not None:
            chroma_meta = err_or_host
        else:
            chroma_meta = err_or_host

    ram, ram_note = _ram_summary()
    net_host, net_avg_ms, net_err, nfs_staging = _network_vital_summary()

    if _RICH:
        _render_rich(
            disk_rows,
            args.collection,
            chroma_count,
            chroma_meta,
            ram,
            ram_note,
            net_host,
            net_avg_ms,
            net_err,
            nfs_staging,
        )
    else:
        print("(install `rich` for a nicer layout: pip install rich)\n")
        _render_ascii(
            disk_rows,
            args.collection,
            chroma_count,
            chroma_meta,
            ram,
            ram_note,
            net_host,
            net_avg_ms,
            net_err,
            nfs_staging,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
