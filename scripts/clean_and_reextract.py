#!/usr/bin/env python3
"""
clean_and_reextract.py
Rebuilds dat_01 (AT Commands), dat_02 (URCs), dat_03 (CME/CMS Errors)
from SIM800 Series_AT Command Manual_V1.01, using proper source sections.

Key differences vs. previous approach:
- AT Commands: extracted from X.2.Y sections only; mode determined from
  "Test Command"/"Read Command"/"Write Command"/"Execution Command" markers
- URCs: extracted ONLY from section 19.3 table
- Error codes: extracted ONLY from section 19.1 (CME) and 19.2 (CMS) tables
"""
from __future__ import annotations
import re, sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("pip install pyyaml"); sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
EX = ROOT / "sources" / "extracted"
NOW = "2026-10-10T00:00:00Z"

AT_TXT = EX / "SIM800 Series_AT Command Manual_V1.01.txt"
if not AT_TXT.exists():
    print(f"ERROR: {AT_TXT} not found"); sys.exit(1)
text = AT_TXT.read_text(encoding="utf-8", errors="ignore")

def cat_from_section(sec):
    m = re.match(r'^(\d+)\.', sec)
    if not m: return "General"
    return {2:"General",3:"Network",4:"SMS",5:"STK",6:"General",7:"GPRS",
            8:"TCP/IP",9:"IP",10:"PING",11:"HTTP",12:"FTP",13:"GPS",
            14:"Email",15:"MMS",16:"Audio",17:"Audio",18:"Audio"}.get(int(m.group(1)),"General")

# ============================================================
# dat_01: AT Commands
# ============================================================
print("Extracting AT commands ...")

header_re = re.compile(
    r'^(?P<sec>\d+(?:\.\d+){1,3})\s+'
    r'(?P<cmd>(?:AT[+&]?[A-Z][A-Z0-9_/]*|A/|ATA|ATD|ATH|ATI|ATL|ATM|ATO|ATP|ATQ|ATS\d+|ATT|ATV|ATX|ATZ))'
    r'\s+(?P<desc>[^\n]+)$',
    re.MULTILINE
)

candidates = []
for m in header_re.finditer(text):
    sec = m.group("sec")
    line = m.group(0)
    if not re.match(r'^\d+\.2(\.\d+){1,2}$', sec):
        continue
    if re.search(r'\.{3,}\s*\d+\s*$', line):
        continue
    desc = m.group("desc").strip()
    if not desc: continue
    candidates.append({"sec":sec,"cmd":m.group("cmd").strip(),
                       "desc":desc,"start":m.start(),"end":m.end()})

# Deduplicate by (sec, cmd)
seen = set(); uniq = []
for c in candidates:
    k = (c["sec"], c["cmd"])
    if k in seen: continue
    seen.add(k); uniq.append(c)

print(f"  Found {len(uniq)} unique AT command sections")

def extract_modes(body):
    modes = []
    if re.search(r'\bTest\s+Command\b', body, re.IGNORECASE): modes.append("test")
    if re.search(r'\bRead\s+Command\b', body, re.IGNORECASE): modes.append("read")
    if re.search(r'\bWrite\s+Command\b', body, re.IGNORECASE): modes.append("write")
    if re.search(r'\bExecution\s+Command\b', body, re.IGNORECASE): modes.append("exec")
    return modes

def extract_syntax(body, cmd):
    lines = body.splitlines()
    for i, ln in enumerate(lines):
        if re.search(r'\b(Write|Test|Read|Execution)\s+Command\b', ln, re.IGNORECASE):
            for j in range(i, min(i+4, len(lines))):
                cand = lines[j].strip()
                if 3 < len(cand) < 120 and (cand.startswith("AT") or cand.startswith(cmd)):
                    return cand
    for ln in lines:
        s = ln.strip()
        if s.startswith("AT") and ("=" in s or "?" in s) and len(s) < 120:
            return s
    return None

def extract_examples(body):
    out = []
    m = re.search(r'\bExample[s]?\s*[:.]', body, re.IGNORECASE)
    if not m: return out
    snippet = body[m.end():m.end()+800]
    for ln in snippet.splitlines()[:20]:
        s = ln.strip()
        if s.startswith("AT") and 3 < len(s) < 200:
            out.append(s)
            if len(out) >= 3: break
    return out

KNOWN_URCS = ["+CMTI","+CMT","+CDS","+CUSD","+CLIP","+CRING","+CREG","+CGREG",
              "+PDP","+CIPRXGET","+HTTPACTION","+FTPGET","+FTPPUT","+SSLRECV",
              "RING","NO CARRIER","+CIPCLOSE","+CIPSTATUS"]

def extract_urcs(body):
    return [u for u in KNOWN_URCS if u in body][:5]

at_records = []
for i, c in enumerate(uniq, start=1):
    idx = uniq.index(c)
    body_start = c["end"]
    body_end = uniq[idx+1]["start"] if idx+1 < len(uniq) else len(text)
    body = text[body_start:body_end][:5000]
    modes = extract_modes(body) or ["exec"]
    syn = extract_syntax(body, c["cmd"])
    examples = extract_examples(body)
    urcs = extract_urcs(body)

    at_records.append({
        "id": f"dat_01_{i:04d}",
        "category": cat_from_section(c["sec"]),
        "command": c["cmd"],
        "mode": modes[0],
        "modes": modes,
        "syntax": syn,
        "description": c["desc"],
        "parameters": [],
        "response_success": "OK",
        "response_error": None,
        "examples": examples,
        "related_urcs": urcs,
        "related_states": [],
        "related_commands": [],
        "firmware_min": None, "firmware_max": None,
        "source": {"name":"SIM800 Series_AT Command Manual","version":"V1.01",
                   "date":"2013-07-23","section":c["sec"]},
        "source_type": "primary",
        "confidence": 0.85 if syn else 0.70,
        "status": "complete" if syn else "partial",
        "conflicts": [],
        "notes": None if syn else "syntax not auto-extracted; needs manual review",
        "tags": [],
        "applicable_models": ["SIM800L"],
        "created_at": NOW, "updated_at": NOW,
    })

DATA.joinpath("dat_01_at_command.yaml").write_text(
    yaml.safe_dump(at_records, allow_unicode=True, sort_keys=False), encoding="utf-8")
print(f"  Wrote {len(at_records)} AT command records")

# ============================================================
# dat_02: URCs from section 19.3
# ============================================================
print("\nExtracting URCs from section 19.3 ...")
s193 = re.search(r'19\.3\s+Summary of Unsolicited Result Codes', text)
s20 = re.search(r'\n\s*20\s+AT Commands Examples', text)
if not s193:
    print("  ERROR: section 19.3 not found"); sys.exit(1)

start = s193.end()
end = s20.start() if s20 else start + 25000
urc_section = text[start:end]

# Table rows start with "+XXX" or uppercase keyword
urc_re = re.compile(
    r'^(\+[A-Z][A-Z0-9_]*|RING|NO CARRIER|NORMAL POWER DOWN|'
    r'UNDER-VOLTAGE [A-Z ]+|OVER-VOLTAGE [A-Z ]+|MO RING|MO CONNECTED|'
    r'RDY|Call Ready|CHARGE-ONLY MODE)'
    r'(?:[^\n]{0,180}?)\s{2,}([^\n]{5,200})',
    re.MULTILINE | re.IGNORECASE
)

urc_records = []
seen_urc = set()
for m in urc_re.finditer(urc_section):
    u = m.group(1).strip()
    desc = m.group(2).strip()
    if u in seen_urc: continue
    if len(u) > 80: continue
    seen_urc.add(u)
    rel = None
    cm = re.search(r'(AT[+&]?[A-Z][A-Z0-9_]*)', desc)
    if cm: rel = cm.group(1)
    urc_records.append({
        "id": f"dat_02_{len(urc_records)+1:04d}",
        "category": "URC",
        "urc_string": u,
        "trigger_event": desc[:200],
        "related_command": rel,
        "related_state": None,
        "format": u,
        "parameters": [],
        "examples": [u],
        "timing": None,
        "suppression_method": None,
        "source": {"name":"SIM800 Series_AT Command Manual","version":"V1.01",
                   "date":"2013-07-23","section":"19.3"},
        "source_type": "primary",
        "confidence": 0.85,
        "status": "complete",
        "conflicts": [], "notes": None,
        "tags": ["urc"],
        "applicable_models": ["SIM800L"],
        "created_at": NOW, "updated_at": NOW,
    })

DATA.joinpath("dat_02_urc.yaml").write_text(
    yaml.safe_dump(urc_records, allow_unicode=True, sort_keys=False), encoding="utf-8")
print(f"  Wrote {len(urc_records)} URC records")

# ============================================================
# dat_03: CME / CMS
# ============================================================
print("\nExtracting error codes ...")

def extract_errs(start_pat, end_pat, expected_min):
    m1 = re.search(start_pat, text)
    if not m1:
        print(f"  WARNING: section {start_pat} not found"); return []
    m2 = re.search(end_pat, text)
    end = m2.start() if m2 else m1.end() + 30000
    sect = text[m1.end():end]
    row_re = re.compile(r'^(\d{1,5})\s+([A-Za-z][^\n]{2,150})$', re.MULTILINE)
    rows = []
    for m in row_re.finditer(sect):
        code = int(m.group(1))
        meaning = m.group(2).strip()
        if code > 9999: continue
        if len(meaning) < 3: continue
        if re.search(r'\.{3,}', meaning): continue
        rows.append((code, meaning))
    print(f"  {len(rows)} rows found (expected >= {expected_min})")
    return rows

cme = extract_errs(r'19\.1\s+Summary of CME ERROR Codes',
                   r'19\.2\s+Summary of CMS ERROR Codes', 50)
cms = extract_errs(r'19\.2\s+Summary of CMS ERROR Codes',
                   r'19\.3\s+Summary of Unsolicited Result Codes', 100)

err_records = []
n = 0
for code, meaning in cme:
    n += 1
    err_records.append({
        "id": f"dat_03_{n:04d}", "category":"CME",
        "error_type":"CME", "code":code, "meaning":meaning,
        "description":meaning, "related_commands":[], "recovery_steps":[],
        "source":{"name":"SIM800 Series_AT Command Manual","version":"V1.01",
                  "date":"2013-07-23","section":"19.1"},
        "source_type":"primary", "confidence":0.95, "status":"complete",
        "conflicts":[], "notes":None, "tags":["cme","error"],
        "applicable_models":["SIM800L"], "created_at":NOW, "updated_at":NOW,
    })
for code, meaning in cms:
    n += 1
    err_records.append({
        "id": f"dat_03_{n:04d}", "category":"CMS",
        "error_type":"CMS", "code":code, "meaning":meaning,
        "description":meaning, "related_commands":[], "recovery_steps":[],
        "source":{"name":"SIM800 Series_AT Command Manual","version":"V1.01",
                  "date":"2013-07-23","section":"19.2"},
        "source_type":"primary", "confidence":0.95, "status":"complete",
        "conflicts":[], "notes":None, "tags":["cms","error"],
        "applicable_models":["SIM800L"], "created_at":NOW, "updated_at":NOW,
    })

DATA.joinpath("dat_03_error_code.yaml").write_text(
    yaml.safe_dump(err_records, allow_unicode=True, sort_keys=False), encoding="utf-8")
print(f"  Wrote {len(err_records)} error code records")

print("\n=== SUMMARY ===")
print(f"  dat_01: {len(at_records)} records")
print(f"  dat_02: {len(urc_records)} records")
print(f"  dat_03: {len(err_records)} records")