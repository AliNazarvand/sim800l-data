# sources/

Place the two primary Hardware Design PDFs here (or in the repository root,
or in `./pdfs/`, or in the parent folder). The preflight script searches all
of those locations.

Required file names (case-insensitive on Windows, exact on Linux):

- `SIM800L_Hardware_Design_V1.00.pdf`
- `SIM800H&SIM800L_Hardware_Design_V2.02.PDF`

Once both files are reachable, run:

```bash
python tools/preflight.py
```

A green result means Phase 1 extraction may begin.