#!/usr/bin/env python3
"""Cross-reference between datasets."""
from __future__ import annotations
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Install pyyaml: pip install pyyaml")
    sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
REPORT = ROOT / "reports" / "CROSS_REF_REPORT.md"


def load(name: str):
    files = sorted(DATA.glob(f"{name}_*.yaml"))
    records = []
    for f in files:
        try:
            data = yaml.safe_load(f.read_text(encoding="utf-8")) or []
            if isinstance(data, list):
                records.extend(data)
        except Exception as e:
            print(f"[warn] {f.name}: {e}")
    return records


def main() -> int:
    dat01 = load("dat_01")
    dat02 = load("dat_02")
    dat03 = load("dat_03")
    dat05 = load("dat_05")
    dat09 = load("dat_09")
    commands = {r.get("command") for r in dat01 if r.get("command")}
    states = {r.get("state_name") for r in dat05 if r.get("state_name")}
    issues = []
    for r in dat09:
        cmd = r.get("command")
        if cmd and cmd not in commands:
            issues.append(f"dat_09 {r.get('id')} {cmd} not in dat_01")
    for r in dat02:
        cmd = r.get("related_command")
        if cmd and cmd not in commands:
            issues.append(f"dat_02 {r.get('id')} {cmd} not in dat_01")
        st = r.get("related_state")
        if st and st not in states and dat05:
            issues.append(f"dat_02 {r.get('id')} {st} not in dat_05")
    for r in dat03:
        for cmd in (r.get("related_commands") or []):
            if cmd and cmd not in commands:
                issues.append(f"dat_03 {r.get('id')} {cmd} not in dat_01")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    with REPORT.open("w", encoding="utf-8") as f:
        f.write("# CROSS_REF_REPORT\n\n")
        if issues:
            f.write(f"Found {len(issues)} issue(s):\n\n")
            for i in issues:
                f.write(f"- {i}\n")
        else:
            f.write("No cross-ref issues.\n")
    for i in issues:
        print(i)
    print(f"\nTotal issues: {len(issues)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())