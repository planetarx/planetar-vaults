# planetar-vaults

A **maritime-domain entity knowledge graph** for the planetar platform — a file-based hyperweb
where the vessel is the hub and every real-world thing it touches (flag state, registry, operating
company, owner, ultimate beneficial owner, captain, cargo, port, incident) is its own entity that
links back and sideways. Modeled on the *entity* side of doi.bio; the durable knowledge layer for
`planetar-ontology`'s live, sensor-resolved graph.

> **Status: Phase 2 LANDED 2026-07-25 — the SQLite index + data-quality report.** (Phase 1 = schema
> + seed, 2026-07-22.) Read [`docs/DESIGN.md`](docs/DESIGN.md) and [`docs/CONVENTIONS.md`](docs/CONVENTIONS.md)
> before authoring. **Public repo — a demonstration, not a public accusation service** (DECISIONS
> V10a): public content is **synthetic/illustrative**; real adverse claims about named parties stay
> out of the public repo and belong in a government-operated deployment.

## Building the index

```
python3 tools/index.py --report data-quality.md   # -> index.db (SQLite) + the report
python3 tools/index.py                             # report to stdout
```
Deps: stdlib `sqlite3` + PyYAML. The index (`entities` / `edges` / `mentions` tables, with per-edge
`status`/`source`) and the derived report are build artifacts (git-ignored) — regenerate on demand.

## What's here now

| Path | State |
|---|---|
| [`docs/DESIGN.md`](docs/DESIGN.md) | ✅ The full design spec (entity model, conventions, collaboration model, vault↔ontology mechanism, governance, phasing) |
| [`docs/CONVENTIONS.md`](docs/CONVENTIONS.md) | ✅ The normative on-disk record format |
| [`CLAUDE.md`](CLAUDE.md) | ✅ Repo guidance |
| [`DECISIONS.md`](DECISIONS.md) | ✅ Filed decisions V1–V11 |
| The nine sub-vaults (`vessels/` … `orgs/`) | ✅ Each with a README stating what it holds + its key |
| Seed cluster (synthetic "Kestrel fleet" + real spokes) | ✅ 14 records exercising every edge type + all four provenance states |
| [`docs/plans/2026-07-22-phase1-schema-and-seed.md`](docs/plans/2026-07-22-phase1-schema-and-seed.md) | ✅ The Phase-1 implementation plan |

## What's coming (Phases 2–4)

The SQLite index + data-quality report (Phase 2), the MCP server + ontology-harvest generator
(Phase 3), and the write-back exporter that enriches the live graph (Phase 4). See
[`docs/DESIGN.md` §7](docs/DESIGN.md). No code yet.
