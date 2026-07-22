# planetar-vaults

A **maritime-domain entity knowledge graph** for the planetar platform — a file-based hyperweb
where the vessel is the hub and every real-world thing it touches (flag state, registry, operating
company, owner, ultimate beneficial owner, captain, cargo, port, incident) is its own entity that
links back and sideways. Modeled on the *entity* side of doi.bio; the durable knowledge layer for
`planetar-ontology`'s live, sensor-resolved graph.

> **Status: DESIGN APPROVED 2026-07-22 — not yet built.** Read [`docs/DESIGN.md`](docs/DESIGN.md)
> before doing anything here. This repo is **private** to start (it will hold sourced but adverse
> claims about named real parties — see §Governance in the design).

## What's here now

| Path | State |
|---|---|
| [`docs/DESIGN.md`](docs/DESIGN.md) | ✅ The full design spec (entity model, conventions, collaboration model, vault↔ontology mechanism, governance, phasing) |

## What's coming (Phase 1)

The nine sub-vaults (`vessels/`, `companies/`, `people/`, `countries/`, `registries/`, `cargo/`,
`ports/`, `cases/`, `orgs/`), a `CONVENTIONS.md`, a `CLAUDE.md`, one fully-worked seed cluster, and
a `DECISIONS.md`. Markdown only, no code — the index + MCP + generators are Phases 2–4. See
[`docs/DESIGN.md` §7](docs/DESIGN.md).
