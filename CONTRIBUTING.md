# Contributing

## Golden rules

1. **Data-only.** No executable code, drivers, or libraries. Python is
   allowed only under `tools/` and only for validation / JSON / preflight.
2. **No hallucination.** Every data record must carry `_meta.source_page`
   and `_meta.source_section` pointing to one of the primary sources. If a
   value is not present in the sources, it must be `null` with
   `_meta.missing_reason` set — never filled from prior knowledge.
3. **YAML is the source of truth.** Generated JSON is never edited by hand.
4. **Schema per dataset.** A dataset is only added once it exists, together
   with `schemas/<dataset>.schema.json` and
   `data/<dataset>/_dataset_meta.yaml`.
5. **Sources.**
   - Phase 1: only the two Hardware Design PDFs.
   - Phase 2a: primary PDFs + AT Command Manual.
   - Phase 2b: as specified by the project plan.

## Allowed `_meta.missing_reason` (record level)

`NOT_FOUND_IN_SOURCES`, `DEFERRED_TO_PHASE_2A`, `DEFERRED_TO_PHASE_2B`,
`CONFLICTING_SOURCES`, `MIXED`.

`INSUFFICIENT_RECORDS` is NOT allowed at the record level — it belongs only
in `_dataset_meta.yaml` (`reason:`).

## Conflict handling (V1.00 vs V2.02)

V2.02 is authoritative. V1.00-only data is retained only when it has
historical/technical value, is tagged with `deprecated_in: "V2.02"` and
`source_version: "V1.00"`, and is logged in `docs/conflict_log.md`.

## Commit messages

English. Conventional Commits style preferred.