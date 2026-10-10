#!/usr/bin/env python3
"""Enhanced validation with semantic checks per dataset."""
from __future__ import annotations
import re, sys
from pathlib import Path
try:
    import yaml
    from jsonschema import Draft7Validator
except ImportError as e:
    print(f"Missing dependency: {e}"); sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SCHEMAS = ROOT / "schemas"
REPORT = ROOT / "reports" / "VALIDATION_REPORT.md"

errors = []

for n in [f"{i:02d}" for i in range(1,19)]:
    sp = SCHEMAS / f"dat_{n}.schema.yaml"
    if not sp.exists():
        errors.append(f"[dat_{n}] schema missing"); continue
    try:
        schema = yaml.safe_load(sp.read_text(encoding="utf-8"))
    except Exception as e:
        errors.append(f"[dat_{n}] schema parse error: {e}"); continue
    validator = Draft7Validator(schema) if schema else None

    for df in sorted(DATA.glob(f"dat_{n}_*.yaml")):
        try:
            records = yaml.safe_load(df.read_text(encoding="utf-8")) or []
        except Exception as e:
            errors.append(f"[{df.name}] YAML parse error: {e}"); continue
        if not isinstance(records, list):
            errors.append(f"[{df.name}] not a list"); continue
        ids = set()
        for i, r in enumerate(records):
            if not isinstance(r, dict):
                errors.append(f"[{df.name}#{i}] not a dict"); continue
            if validator:
                for err in validator.iter_errors(r):
                    errors.append(f"[{df.name}#{i}] schema: {err.message}")
            rid = r.get("id")
            if rid in ids: errors.append(f"[{df.name}#{i}] dup id: {rid}")
            ids.add(rid)
            if "SIM800L" not in (r.get("applicable_models") or []):
                errors.append(f"[{df.name}#{i}] missing SIM800L")
            if r.get("status") == "example-only":
                errors.append(f"[{df.name}#{i}] example-only forbidden")
            src = r.get("source")
            if not isinstance(src, dict) or not src.get("name"):
                errors.append(f"[{df.name}#{i}] missing source.name")

            if n == "01":
                cmd = r.get("command") or ""
                if not re.match(r'^(AT|A/|ATA|ATD|ATH|ATI|ATL|ATM|ATO|ATP|ATQ|ATT|ATV|ATX|ATZ)', cmd):
                    errors.append(f"[{df.name}#{i}] bad command form: {cmd}")
                md = r.get("mode")
                if md not in ("test","read","write","exec",None):
                    errors.append(f"[{df.name}#{i}] bad mode: {md}")
                syn = r.get("syntax") or ""
                if "...." in syn:
                    errors.append(f"[{df.name}#{i}] syntax has ToC dots")
                nts = r.get("notes") or ""
                if "...." in nts and re.search(r'\d{2,4}\s*$', nts):
                    errors.append(f"[{df.name}#{i}] notes looks like ToC")

            if n == "02":
                u = r.get("urc_string") or ""
                if not (u.startswith("+") or re.match(r'^[A-Z][A-Z0-9 \-]{2,}$', u) or u in ("RING",)):
                    errors.append(f"[{df.name}#{i}] urc_string not URC-like: {u}")

            if n == "03":
                if r.get("error_type") not in ("CME","CMS"):
                    errors.append(f"[{df.name}#{i}] bad error_type")
                c = r.get("code")
                if not isinstance(c, int) or c < 0 or c > 9999:
                    errors.append(f"[{df.name}#{i}] bad code: {c}")

REPORT.parent.mkdir(parents=True, exist_ok=True)
with REPORT.open("w", encoding="utf-8") as f:
    f.write("# VALIDATION_REPORT\n\n")
    if errors:
        f.write(f"Found {len(errors)} issue(s):\n\n")
        for e in errors[:500]: f.write(f"- {e}\n")
    else:
        f.write("All checks passed.\n")

for e in errors[:50]: print(e)
print(f"\nTotal issues: {len(errors)}")
print(f"Report: {REPORT}")
sys.exit(1 if errors else 0)