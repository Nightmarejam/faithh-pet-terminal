#!/usr/bin/env python3
"""Summarize UniFi read-only API snapshots into markdown and CSV."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return None


def flatten_target(target: dict[str, Any]) -> str:
    if not isinstance(target, dict):
        return ""
    pieces: list[str] = []
    mt = target.get("matching_target")
    if mt:
        pieces.append(f"target={mt}")
    mtt = target.get("matching_target_type")
    if mtt:
        pieces.append(f"type={mtt}")
    zone = target.get("zone_id")
    if zone:
        pieces.append(f"zone={zone}")
    port = target.get("port")
    if port:
        pieces.append(f"port={port}")
    port_mode = target.get("port_matching_type")
    if port_mode:
        pieces.append(f"port_mode={port_mode}")
    ips = target.get("ips") or []
    if ips:
        pieces.append("ips=" + ",".join(map(str, ips)))
    nets = target.get("network_ids") or []
    if nets:
        pieces.append("nets=" + ",".join(map(str, nets)))
    domains = target.get("web_domains") or []
    if domains:
        pieces.append("domains=" + ",".join(map(str, domains)))
    return " | ".join(pieces)


def latest_snapshot_dir(base: Path) -> Path:
    candidates = sorted([p for p in base.glob("snapshot_*") if p.is_dir()])
    if not candidates:
        raise FileNotFoundError(f"No snapshot_* directories found under {base}")
    return candidates[-1]


def parse_iso_date(value: str) -> datetime | None:
    """Parse YYYY-MM-DD (and tolerate full ISO timestamps) to datetime."""
    if not value:
        return None
    try:
        if len(value) == 10:
            return datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=UTC)
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=UTC)
        return parsed
    except ValueError:
        return None


def detect_stale_reason(rule: dict[str, Any], now: datetime) -> str:
    """Return non-empty reason when rule appears stale."""
    schedule = rule.get("schedule")
    if not isinstance(schedule, dict):
        return ""

    date_end = parse_iso_date(str(schedule.get("date_end", "")))
    if date_end and date_end < now:
        return f"schedule_end_passed:{date_end.date().isoformat()}"

    date_start = parse_iso_date(str(schedule.get("date_start", "")))
    if date_start and date_start > now:
        return f"schedule_not_started:{date_start.date().isoformat()}"

    return ""


def classify_custom_rules(
    rules: list[dict[str, Any]], now: datetime
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Split into active and disabled/stale custom rules."""
    active: list[dict[str, Any]] = []
    disabled_or_stale: list[dict[str, Any]] = []

    for rule in rules:
        stale_reason = detect_stale_reason(rule, now)
        enabled = bool(rule.get("enabled", False))
        rule["_stale_reason"] = stale_reason
        rule["_stale"] = bool(stale_reason)

        if enabled and not stale_reason:
            active.append(rule)
        else:
            disabled_or_stale.append(rule)

    return active, disabled_or_stale


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize UniFi API snapshot files.")
    parser.add_argument(
        "--snapshot-dir",
        help="Path to snapshot_<timestamp> directory. Defaults to latest under reports/security/unifi_api.",
    )
    parser.add_argument(
        "--output-md",
        help="Optional markdown output path. Defaults to <snapshot_dir>/policy_inventory.md",
    )
    parser.add_argument(
        "--output-csv",
        help="Optional CSV output path. Defaults to <snapshot_dir>/policy_inventory.csv",
    )
    args = parser.parse_args()

    if args.snapshot_dir:
        snapshot_dir = Path(args.snapshot_dir).resolve()
    else:
        snapshot_dir = latest_snapshot_dir(
            Path("/home/jonat/ai-stack/reports/security/unifi_api").resolve()
        )

    if not snapshot_dir.exists():
        raise FileNotFoundError(f"Snapshot directory not found: {snapshot_dir}")

    trafficrules_path = snapshot_dir / "proxy_network_v2_api_site_default_trafficrules.json"
    firewall_policies_path = snapshot_dir / "proxy_network_v2_api_site_default_firewall-policies.json"
    summary_path = snapshot_dir / "summary.txt"

    traffic_rules = load_json(trafficrules_path) or []
    firewall_policies = load_json(firewall_policies_path) or []
    summary_text = summary_path.read_text() if summary_path.exists() else "summary.txt missing"

    if not isinstance(traffic_rules, list):
        traffic_rules = []
    if not isinstance(firewall_policies, list):
        firewall_policies = []

    now_dt = datetime.now(UTC)

    custom_traffic = [r for r in traffic_rules if isinstance(r, dict) and not r.get("predefined", False)]
    active_custom_traffic, disabled_or_stale_custom_traffic = classify_custom_rules(custom_traffic, now_dt)

    custom_firewall = [r for r in firewall_policies if isinstance(r, dict) and not r.get("predefined", False)]
    active_custom_firewall, disabled_or_stale_custom_firewall = classify_custom_rules(custom_firewall, now_dt)

    port_forward_rules = [
        r
        for r in firewall_policies
        if isinstance(r, dict)
        and (r.get("origin_type") == "port_forward" or "port forward" in str(r.get("name", "")).lower())
    ]

    now = now_dt.isoformat(timespec="seconds") + "Z"
    out_md = Path(args.output_md).resolve() if args.output_md else snapshot_dir / "policy_inventory.md"
    out_csv = Path(args.output_csv).resolve() if args.output_csv else snapshot_dir / "policy_inventory.csv"

    md_lines: list[str] = []
    md_lines.append("# UniFi Policy Inventory")
    md_lines.append("")
    md_lines.append(f"- Generated: `{now}`")
    md_lines.append(f"- Snapshot: `{snapshot_dir}`")
    md_lines.append("")
    md_lines.append("## Endpoint status")
    md_lines.append("")
    md_lines.append("```text")
    md_lines.append(summary_text.rstrip())
    md_lines.append("```")
    md_lines.append("")
    md_lines.append("## Counts")
    md_lines.append("")
    md_lines.append(
        f"- Custom traffic rules: `{len(custom_traffic)}` "
        f"(active `{len(active_custom_traffic)}`, disabled/stale `{len(disabled_or_stale_custom_traffic)}`)"
    )
    md_lines.append(
        f"- Custom firewall policies: `{len(custom_firewall)}` "
        f"(active `{len(active_custom_firewall)}`, disabled/stale `{len(disabled_or_stale_custom_firewall)}`)"
    )
    md_lines.append(f"- Port-forward-derived firewall entries: `{len(port_forward_rules)}`")
    md_lines.append("")
    md_lines.append("## Stale detection")
    md_lines.append("")
    md_lines.append("- Rule is marked stale when schedule date window appears inactive (ended or not started).")
    md_lines.append("- Disabled/stale sections include disabled rules and schedule-stale rules.")
    md_lines.append("")

    def add_rule_table(title: str, rows: list[dict[str, Any]]) -> None:
        md_lines.append(f"## {title}")
        md_lines.append("")
        if not rows:
            md_lines.append("_None_")
            md_lines.append("")
            return
        md_lines.append("| Name | Enabled | Stale | Stale Reason | Action | Protocol | Source | Destination |")
        md_lines.append("|------|---------|-------|--------------|--------|----------|--------|-------------|")
        for r in rows:
            name = str(r.get("name", "")).replace("|", "/")
            enabled = "yes" if r.get("enabled") else "no"
            stale = "yes" if r.get("_stale") else "no"
            stale_reason = str(r.get("_stale_reason", "")).replace("|", "/")
            action = str(r.get("action", ""))
            protocol = str(r.get("protocol", ""))
            source = flatten_target(r.get("source", {})).replace("|", "/")
            dest = flatten_target(r.get("destination", {})).replace("|", "/")
            md_lines.append(
                f"| {name} | {enabled} | {stale} | {stale_reason} | {action} | {protocol} | {source} | {dest} |"
            )
        md_lines.append("")

    add_rule_table("Active Custom Traffic Rules", active_custom_traffic)
    add_rule_table("Disabled/Stale Custom Traffic Rules", disabled_or_stale_custom_traffic)
    add_rule_table("Active Custom Firewall Policies", active_custom_firewall)
    add_rule_table("Disabled/Stale Custom Firewall Policies", disabled_or_stale_custom_firewall)
    add_rule_table("Port-Forward-Derived Firewall Entries", port_forward_rules)

    out_md.write_text("\n".join(md_lines) + "\n")

    csv_rows: list[dict[str, str]] = []
    for section, rows in [
        ("active_custom_traffic", active_custom_traffic),
        ("disabled_or_stale_custom_traffic", disabled_or_stale_custom_traffic),
        ("active_custom_firewall", active_custom_firewall),
        ("disabled_or_stale_custom_firewall", disabled_or_stale_custom_firewall),
        ("port_forward", port_forward_rules),
    ]:
        for r in rows:
            csv_rows.append(
                {
                    "section": section,
                    "name": str(r.get("name", "")),
                    "enabled": str(bool(r.get("enabled", False))),
                    "action": str(r.get("action", "")),
                    "protocol": str(r.get("protocol", "")),
                    "index": str(r.get("index", "")),
                    "origin_type": str(r.get("origin_type", "")),
                    "stale": str(bool(r.get("_stale", False))),
                    "stale_reason": str(r.get("_stale_reason", "")),
                    "source": flatten_target(r.get("source", {})),
                    "destination": flatten_target(r.get("destination", {})),
                }
            )

    with out_csv.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "section",
                "name",
                "enabled",
                "action",
                "protocol",
                "index",
                "origin_type",
                "stale",
                "stale_reason",
                "source",
                "destination",
            ],
        )
        writer.writeheader()
        writer.writerows(csv_rows)

    print(f"Markdown report: {out_md}")
    print(f"CSV report: {out_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
