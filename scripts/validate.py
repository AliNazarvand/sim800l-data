#!/usr/bin/env python3
"""Validate all dat_*.yaml against schemas/dat_*.schema.yaml."""
from __future__ import annotations
import sys
from pathlib import Path

try:
    import yaml
    from jsonschema import Draft7Validator
except ImportError as e:
    print(f"Missing dependency: {e}. Install: pip install pyyaml jsonschema")
    sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
SCHEMA_DIR = ROOT / "schemas"
REPORT = ROOT / "reports" / "VALIDATION_REPORT.md"


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate_dataset(num: str) -> list:
    errors = []
    schema_path = SCHEMA_DIR / f"dat_{num}.schema.yaml"
    if not schema_path.exists():
        errors.append(f"[dat_{num}] schema missing")
        return errors
    data_files = sorted(DATA_DIR.glob(f"dat_{num}_*.yaml"))
    if not data_files:
        errors.append(f"[dat_{num}] no data file")
        return errors
    schema = load_yaml(schema_path)
    validator = Draft7Validator(schema)
    for df in data_files:
        try:
            records = load_yaml(df) or []
        except Exception as e:
            errors.append(f"[{df.name}] YAML parse error: {e}")
            continue
        if not isinstance(records, list):
            errors.append(f"[{df.name}] top-level not a list")
            continue
        ids = set()
        for i, rec in enumerate(records):
            if not isinstance(rec, dict):
                errors.append(f"[{df.name}#{i}] not a mapping")
                continue
            for err in validator.iter_errors(rec):
                errors.append(f"[{df.name}#{i}] {err.message}")
            if rec.get("status") == "example-only":
                errors.append(f"[{df.name}#{i}] example-only in data/")
            rid = rec.get("id")
            if rid in ids:
                errors.append(f"[{df.name}#{i}] duplicate id: {rid}")
            ids.add(rid)
            if "SIM800L" not in (rec.get("applicable_models") or []):
                errors.append(f"[{df.name}#{i}] missing SIM800L")
    return errors


def main() -> int:
    all_errors = []
    for n in [f"{i:02d}" for i in range(1, 19)]:
        all_errors.extend(validate_dataset(n))
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    with REPORT.open("w", encoding="utf-8") as f:
        f.write("# VALIDATION_REPORT\n\n")
        if all_errors:
            f.write(f"Found {len(all_errors)} issue(s):\n\n")
            for e in all_errors:
                f.write(f"- {e}\n")
        else:
            f.write("All checks passed.\n")
    for e in all_errors:
        print(e)
    print(f"\nTotal issues: {len(all_errors)}")
    return 0 if not all_errors else 1


if __name__ == "__main__":
    sys.exit(main())