#!/usr/bin/env python3
"""G4 switch controller: toggle faithh between inference and mining modes."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CmdResult:
    command: str
    returncode: int
    stdout: str
    stderr: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Switch FAITHH VM between inference (vLLM) and mining."
    )
    parser.add_argument(
        "--target",
        required=True,
        choices=["inference", "mining", "auto"],
        help="Desired target mode. 'auto' derives mode from signals file.",
    )
    parser.add_argument(
        "--faithh-host",
        default=os.environ.get("FAITHH_HOST", "faithh.taileb8c60.ts.net"),
        help="faithh VM hostname/IP.",
    )
    parser.add_argument(
        "--faithh-user",
        default=os.environ.get("FAITHH_USER", "jonat"),
        help="SSH username for faithh VM.",
    )
    parser.add_argument(
        "--signals-file",
        default=str(
            Path(__file__).resolve().parents[1] / "data" / "signals" / "latest_signals.json"
        ),
        help="Signals file used for --target auto mode.",
    )
    parser.add_argument(
        "--auto-min-opportunities",
        type=int,
        default=1,
        help="For auto mode: if opportunities >= this value, choose inference; else mining.",
    )
    parser.add_argument(
        "--miner-start-cmd",
        default=os.environ.get("MINER_START_CMD", ""),
        help="Remote command on faithh to start miner process.",
    )
    parser.add_argument(
        "--miner-stop-cmd",
        default=os.environ.get(
            "MINER_STOP_CMD",
            "pkill -f lolminer || true; pkill -f t-rex || true; pkill -f trex || true",
        ),
        help="Remote command on faithh to stop miner process.",
    )
    parser.add_argument(
        "--require-gpu-free",
        action="store_true",
        help=(
            "For mining mode, fail if NVIDIA reports active compute processes "
            "after vLLM stop."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands without executing them.",
    )
    return parser.parse_args()


def run_local(command: list[str]) -> CmdResult:
    proc = subprocess.run(command, capture_output=True, text=True)
    return CmdResult(
        command=" ".join(shlex.quote(p) for p in command),
        returncode=proc.returncode,
        stdout=proc.stdout.strip(),
        stderr=proc.stderr.strip(),
    )


def run_remote(host: str, user: str, remote_command: str, dry_run: bool) -> CmdResult:
    ssh_cmd = ["ssh", f"{user}@{host}", remote_command]
    if dry_run:
        return CmdResult(
            command=" ".join(shlex.quote(p) for p in ssh_cmd),
            returncode=0,
            stdout="dry-run",
            stderr="",
        )
    return run_local(ssh_cmd)


def derive_auto_target(signals_file: Path, min_opportunities: int) -> str:
    payload = json.loads(signals_file.read_text(encoding="utf-8"))
    opportunities = payload.get("opportunities", [])
    return "inference" if len(opportunities) >= min_opportunities else "mining"


def gpu_compute_processes(host: str, user: str, dry_run: bool) -> list[str]:
    result = run_remote(
        host=host,
        user=user,
        remote_command=(
            "nvidia-smi --query-compute-apps=pid,process_name,used_gpu_memory "
            "--format=csv,noheader || true"
        ),
        dry_run=dry_run,
    )
    if dry_run:
        return []
    if not result.stdout.strip():
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def main() -> int:
    args = parse_args()
    target = args.target
    if target == "auto":
        signals_path = Path(args.signals_file).expanduser().resolve()
        if not signals_path.exists():
            raise FileNotFoundError(f"Signals file missing for auto mode: {signals_path}")
        target = derive_auto_target(
            signals_file=signals_path,
            min_opportunities=args.auto_min_opportunities,
        )
        print(f"Auto mode selected target={target} from {signals_path}")

    results: list[CmdResult] = []

    if target == "inference":
        # Inference mode: stop miner and ensure vLLM service is running.
        stop_result = run_remote(
            host=args.faithh_host,
            user=args.faithh_user,
            remote_command=args.miner_stop_cmd,
            dry_run=args.dry_run,
        )
        if stop_result.returncode != 0:
            stop_result = CmdResult(
                command=stop_result.command,
                returncode=0,
                stdout=(
                    (stop_result.stdout + "\n") if stop_result.stdout else ""
                )
                + "miner stop command returned non-zero; continuing.",
                stderr=stop_result.stderr,
            )
        results.append(stop_result)
        results.append(
            run_remote(
                host=args.faithh_host,
                user=args.faithh_user,
                remote_command="sudo systemctl start faithh-vllm.service",
                dry_run=args.dry_run,
            )
        )
        results.append(
            run_remote(
                host=args.faithh_host,
                user=args.faithh_user,
                remote_command="sudo systemctl is-active faithh-vllm.service",
                dry_run=args.dry_run,
            )
        )
    elif target == "mining":
        # Mining mode: stop vLLM and optionally start miner command.
        results.append(
            run_remote(
                host=args.faithh_host,
                user=args.faithh_user,
                remote_command="sudo systemctl stop faithh-vllm.service",
                dry_run=args.dry_run,
            )
        )
        state_result = run_remote(
            host=args.faithh_host,
            user=args.faithh_user,
            remote_command="sudo systemctl is-active faithh-vllm.service || true",
            dry_run=args.dry_run,
        )
        results.append(state_result)

        if not args.dry_run:
            state = state_result.stdout.strip()
            if state == "active":
                results.append(
                    CmdResult(
                        command="verify-vllm-stopped",
                        returncode=1,
                        stdout="",
                        stderr="vLLM service still active after stop command.",
                    )
                )

            if args.require_gpu_free:
                procs = gpu_compute_processes(
                    host=args.faithh_host,
                    user=args.faithh_user,
                    dry_run=False,
                )
                if procs:
                    results.append(
                        CmdResult(
                            command="verify-gpu-free",
                            returncode=1,
                            stdout="",
                            stderr=(
                                "GPU still has active compute processes after vLLM stop: "
                                + "; ".join(procs)
                            ),
                        )
                    )

        if args.miner_start_cmd:
            results.append(
                run_remote(
                    host=args.faithh_host,
                    user=args.faithh_user,
                    remote_command=args.miner_start_cmd,
                    dry_run=args.dry_run,
                )
            )
        else:
            msg = (
                "MINER_START_CMD not provided; skipping miner start. "
                "Pass --miner-start-cmd or set MINER_START_CMD env."
            )
            results.append(CmdResult(command="miner-start", returncode=0, stdout=msg, stderr=""))

    failed = [r for r in results if r.returncode != 0]
    for r in results:
        print(f"$ {r.command}")
        if r.stdout:
            print(r.stdout)
        if r.stderr:
            print(r.stderr)

    if failed:
        print(f"Switch completed with {len(failed)} failed command(s).")
        return 1

    print(f"Switch to target={target} completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
