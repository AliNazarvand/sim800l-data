# sim800l-data

Data-driven dataset collection for the **SIM800L** module.

## Structure
- data/ - 18 YAML datasets (dat_01 .. dat_18)
- schemas/ - JSON-schema for each dataset
- sources/ - original and extracted PDFs
- reports/ - coverage, source inventory, gap, cross-ref, validation, decisions, session, role-map, per-dataset reports
- scripts/ - validate.py, extract_pdf.py, cross_ref.py, ocr_pdf.py

## Quick start
    pip install -r requirements.txt
    python scripts/extract_pdf.py
    python scripts/validate.py
    python scripts/cross_ref.py

## Datasets
| ID | Name |
|---|---|
| dat_01 | AT Command DB |
| dat_02 | URC DB |
| dat_03 | Error Code DB (CME/CMS) |
| dat_04 | Timing & Timeout DB |
| dat_05 | State Machine DB |
| dat_06 | Init Sequence DB |
| dat_07 | Hardware Reference DB |
| dat_08 | Firmware Compatibility Matrix |
| dat_09 | SMS DB |
| dat_10 | GPRS/Data DB |
| dat_11 | HTTP/FTP/SSL DB |
| dat_12 | Audio DB |
| dat_13 | SIM Management DB |
| dat_14 | Operator/APN DB (MCC/MNC) |
| dat_15 | Power Management DB |
| dat_16 | Board/EVB Definitions |
| dat_17 | Certificate/Key Store |
| dat_18 | Certification Data |

## Rules
- Only SIM800L data. Never mix SIM800H/SIM900/SIM7000.
- Every record must have source.
- Prefer V2.02 over V1.00.
- No synthetic data. No example-only in data/.