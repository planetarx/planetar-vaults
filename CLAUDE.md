# CLAUDE.md

Guidance for Claude Code when working in this repository.

## What this repo is

`planetar-vaults` is a **maritime-domain entity knowledge graph** for the planetar platform — a
file-based hyperweb where the vessel is the hub and every real-world thing it touches (flag state,
registry, operator, owner, UBO, captain, cargo, port, incident) is its own linked entity. It is the
**durable knowledge layer** for `planetar-ontology`'s live, sensor-resolved graph. **Markdown only in
Phase 1 — no code, no build, no tests.** The index + MCP + generators are Phases 2–4.

**Read [`docs/DESIGN.md`](docs/DESIGN.md) (the approved design) and [`docs/CONVENTIONS.md`](docs/CONVENTIONS.md)
(the on-disk rules) before authoring anything.**

## Git layout

This directory *is* the git repo; sub-vaults are plain directories (same exception as
`../planetar-grants`). Commit here. Remote: `git@github.com:planetarx/planetar-vaults.git`.

**The repo is PUBLIC — it is a demonstration, not a public accusation service** (DECISIONS V10a).
Keep public content **synthetic/illustrative**; the schema and methodology are the point. **Real
adverse claims about named real parties stay OUT of the public repo** — they belong in a
government-operated deployment. Any real fact added to the public demo must be public-record /
official / externally-reported and sourced+hedged via `status`/`source`/`cases`.

## The nine sub-vaults

`vessels/` `companies/` `people/` `countries/` `registries/` `cargo/` `ports/` `cases/` `orgs/` —
one directory per entity, keyed per `docs/CONVENTIONS.md`. Each sub-vault's `README.md` states what it
holds and its key.

## Authoring rules (the load-bearing ones)

- **Provenance on every fact** — bare value = `inferred`; use the `{target,status,by,at,source,note}`
  object when a human confirms/corrects, or when conflicting assertions must be kept (`disputed`).
- **The machine never clobbers a human.** A generator (Phases 3–4) only writes `inferred` facts and
  treats `confirmed`/`corrected`/human-`by` facts as read-only. When authoring by hand, mark your
  edits `confirmed`/`corrected` with `by:` so future generators respect them.
- **"Why of interest" lives in `cases/`** — dated, sourced, linking the parties — never as a bare
  adverse attribute on a person or company.
- **Real vs synthetic** — countries/registries/ports/cargo/orgs are real; vessels/companies/people/
  cases are synthetic in Phase 1 and carry `synthetic: true` + a caveat line.
- **Wikilinks** are always `[[subvault:id|display]]`. Unresolved = TODO, not error.

## Workspace norms (inherited from ../CLAUDE.md)

Provenance over polish; conservative claims; dates absolute (`2026-07-22`); patent framing
"applicant-named inventor on US Patent 10,936,582" (never ownership).
