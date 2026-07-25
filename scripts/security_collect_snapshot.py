#!/usr/bin/env python3
"""Collect a reproducible security hardening snapshot."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path


def run_cmd(cmd: list[str], timeout: int = 20) -> dict[str, object]:
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return {
            "cmd": cmd,
            "exit_code": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
        }
    except Exception as exc:  # pragma: no cover
        return {
            "cmd": cmd,
            "error": str(exc),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect security hardening snapshot.")
    parser.add_argument(
        "--output-dir",
        default="reports/security",
        help="Output directory for security snapshot artifacts.",
    )
    parser.add_argument(
        "--gen8-host",
        default="gen8",
        help="SSH host alias for Gen8 server.",
    )
    args = parser.parse_args()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    snapshot: dict[str, object] = {
        "snapshot_id": f"security_hardening_{ts}",
        "generated_at": datetime.now().isoformat(),
        "local": {},
        "gen8": {},
    }

    local_cmds = {
        "identity": ["bash", "-lc", "whoami && hostname && uname -a"],
        "listening_ports": ["bash", "-lc", "ss -tulpen"],
        "ufw_status": [
            "bash",
            "-lc",
            "if command -v ufw >/dev/null 2>&1; then ufw status verbose; else echo 'ufw not installed'; fi",
        ],
        "fail2ban_status": [
            "bash",
            "-lc",
            "if command -v fail2ban-client >/dev/null 2>&1; then fail2ban-client status; else echo 'fail2ban not installed'; fi",
        ],
    }
    for key, cmd in local_cmds.items():
        snapshot["local"][key] = run_cmd(cmd)

    gen8_cmds = {
        "connectivity": ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", args.gen8_host, "echo OK && hostname && uname -a"],
        "listening_ports": ["ssh", "-o", "BatchMode=yes", args.gen8_host, "ss -tuln"],
        "docker_ports": [
            "ssh",
            "-o",
            "BatchMode=yes",
            args.gen8_host,
            "docker ps --format 'table {{.Names}}\\t{{.Image}}\\t{{.Ports}}'",
        ],
        "ufw_status": [
            "ssh",
            "-o",
            "BatchMode=yes",
            args.gen8_host,
            "if command -v ufw >/dev/null 2>&1; then sudo -n ufw status verbose || echo 'sudo required for ufw status'; else echo 'ufw not installed'; fi",
        ],
        "fail2ban_status": [
            "ssh",
            "-o",
            "BatchMode=yes",
            args.gen8_host,
            "if command -v fail2ban-client >/dev/null 2>&1; then sudo -n fail2ban-client status || echo 'sudo required for fail2ban status'; else echo 'fail2ban not installed'; fi",
        ],
    }
    for key, cmd in gen8_cmds.items():
        snapshot["gen8"][key] = run_cmd(cmd)

    json_path = output_dir / f"security_hardening_snapshot_{ts}.json"
    json_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")

    md_lines = [
        f"# Security Hardening Snapshot — {ts}",
        "",
        f"- Generated: `{snapshot['generated_at']}`",
        f"- Snapshot ID: `{snapshot['snapshot_id']}`",
        "",
        "## Local",
    ]
    for key, result in snapshot["local"].items():
        md_lines.append(f"### {key}")
        md_lines.append(f"- Exit code: `{result.get('exit_code', 'n/a')}`")
        out = (result.get("stdout", "") or "").strip()
        if out:
            md_lines.append("```")
            md_lines.append(out[:4000])
            md_lines.append("```")
        err = (result.get("stderr", "") or "").strip()
        if err:
            md_lines.append("- stderr:")
            md_lines.append("```")
            md_lines.append(err[:1000])
            md_lines.append("```")

    md_lines.append("")
    md_lines.append("## Gen8")
    for key, result in snapshot["gen8"].items():
        md_lines.append(f"### {key}")
        md_lines.append(f"- Exit code: `{result.get('exit_code', 'n/a')}`")
        out = (result.get("stdout", "") or "").strip()
        if out:
            md_lines.append("```")
            md_lines.append(out[:4000])
            md_lines.append("```")
        err = (result.get("stderr", "") or "").strip()
        if err:
            md_lines.append("- stderr:")
            md_lines.append("```")
            md_lines.append(err[:1000])
            md_lines.append("```")

    md_path = output_dir / f"security_hardening_snapshot_{ts}.md"
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(json_path)
    print(md_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
