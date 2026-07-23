# planetar-vaults — design spec

**Status:** design approved 2026-07-22 (brainstormed with the founder). Phase 1 not yet built.
**Author of record:** Steven Ness / Zax Analytics.
**Repo:** `~/github/planetarx/planetar-vaults` (a new top-level project in the planetar
workspace; **private** to start — see §Governance).

---

## 1. What this is

`planetar-vaults` is a **maritime-domain entity knowledge graph**: a file-based hyperweb where
the **vessel** is the hub and every real-world thing it touches — flag state, registry, operating
company, owner, ultimate beneficial owner, captain, cargo, port, incident — is its own entity
that links back and sideways. It is modeled on the *entity* side of doi.bio (protein ↔ structure
↔ paper ↔ researcher), **not** the docs side: entities connect to each other, not everything to
a central document.

The point is the traversal, which is also the platform's own thesis:

> *this vessel → operated by this company → which runs five others → three of which went dark in
> the same closed area* — that is a vault query, not a sensor reading.

Each entity is a **directory with a main `index.md` plus resources** (track snapshots, SAR chips,
raw source JSON, photos). Entities cross-link with `[[subvault:id|display]]` wikilinks. A SQLite
index and an MCP server (later phases) make the graph queryable by humans and by Claude.

### 1.1 Relationship to what already exists

| Thing | What it is | How the vault relates |
|---|---|---|
| `planetar-ontology` | The **live, sensor-resolved** entity graph, keyed by MMSI, ephemeral, runtime | The vault is the ontology's **durable knowledge layer** (§6): it seeds *from* the ontology and writes *vetted* knowledge *back into* it |
| `planetar-grants` | Dir-per-funding-opportunity workspace | Same repo shape (one git repo, plain sub-directories); different content |
| `~/data/vaults/docs` | The design-doc vault (ARCH-*, DEPLOY-*, ROADMAP-*) | A possible *later* sub-vault leg (§7 Phase 5), not Phase 1 |
| doi.bio vaults | The bio hyperweb the pattern is borrowed from | Method donor; no content reuse. The indexer + MCP core are forkable (§7) |

The vault is a **different kind of thing** from the ontology: the ontology knows a vessel exists
because a sensor saw it; the vault knows **who the vessel really is** — the layer a single sensor
hit can never give you.

---

## 2. Entity model

Nine sub-vaults, each a directory of dir-per-entity records. Keys align to **authoritative
maritime registers** so records are seedable from Equasis/GISIS and joinable to outside data.

| Sub-vault | Entity | Key (permanent ID) | Notes |
|---|---|---|---|
| `vessels/` | a ship | **IMO number** (7 digits, hull-life) | MMSI is a *field*, not the key — it is mutable |
| `companies/` | operator / registered owner / manager / parent / **class society** / **P&I club** | **IMO company & registered-owner number** (`imo-NNNNNNN`), else slug | Class societies and insurers are role-tagged companies, not their own types |
| `people/` | captain / owner / UBO / officer | slug | |
| `countries/` | flag **state** | ISO 3166-1 alpha-2 | |
| `registries/` | the registering **body** (distinct from the country) | slug | Open/second/**fraudulent** registries; a fraudulent registry links to *no* country |
| `cargo/` | commodity or specific cargo | slug | |
| `ports/` | registry / call / destination port | UN/LOCODE | |
| `cases/` | a dark-vessel event, detention, IUU incident | `YYYY-slug` | Where "why of interest" lives — dated, sourced, links the parties |
| `orgs/` | RFMOs & authorities (ICCAT, IOTC…) | slug | Targets of `authorized_by` |

### 2.1 Three modeling decisions (researched 2026-07-21)

1. **Classification societies → role-tagged companies, not a new type.** A closed ~12-member set
   (IACS) that behaves exactly like companies. The load-bearing fact is the vessel's **class
   status over time** (`in class` / `suspended` / `withdrawn` + date) — loss of class is a
   top-tier dark-fleet risk signal (uninsurable, uncharterable, unwelcome at major ports). So:
   society = company (role); class status = a dated edge on the vessel. **P&I clubs** get the
   same treatment (`insured_by`; loss of insurance is the parallel signal).
2. **Registries → their own lightweight type, distinct from `countries`.** A flag *state* is a
   country; a *registry* is the body that grants nationality. **Fraudulent registries** (~a dozen
   operating, growing under sanctions pressure) claim to register on behalf of a state with no
   legal mandate — they cannot hang off a legitimate country node. Registry-/flag-hopping is
   first-class IUU behaviour. So `flagged_under` → country, `registered_in` → registry, registry
   `on_behalf_of` → country (or nothing, when fake).
3. **Ownership "networks" → not an entity; reify the edges.** Per FollowTheMoney (the model
   behind OpenSanctions / OCCRP / Aleph), a network is just the transitive closure of ownership
   edges. Each ownership edge carries `ownershipType` (`registered` / `beneficial` / `ultimate` /
   `direct` / `indirect`), `percentage`, `start`/`end`, `source`. When a specific structure is
   itself the finding, that is a `case`.

### 2.2 Vocabulary — align to FollowTheMoney (FTM)

Borrow FTM property/relationship names wherever they map (`schema: Vessel|Company|Person`,
`imoNumber`, `mmsi`, `callSign`, `flag`, `pastNames`, `Ownership`, `ownershipType`,
`Directorship`, `Sanction`), inventing only for the planetar-specific bits (`cases`, the
`ontology:` join, sensor links). This keeps the door open to ingest/cross-reference OpenSanctions
data later without a translation layer.

### 2.3 Relationship vocabulary (the indexed edges)

`flagged_under` (→country) · `registered_in` (→registry) · `on_behalf_of` (registry→country) ·
`operated_by` · `owned_by` · `managed_by` · `insured_by` (all →company) ·
`beneficially_owned_by` (→company/person) · `captained_by` (→person) · `carries` (→cargo) ·
`bound_for` / `home_port` (→port) · `authorized_by` (→org, with status+dates — RFMO fishing
authorizations) · `same_as` / `formerly` (→vessel, **carry the changed attribute + date**;
this is the re-identification mechanism) · `sister_of` (→vessel) · `parent_of` /
`subsidiary_of` (company→company) · `officer_of` (person→company) · `involves` (case→any).

Ownership relationships (`owned_by`, `beneficially_owned_by`, `operated_by`, `managed_by`) are
**reified** — see §3.

**Class is represented as the vessel's `classStatus`** — a dated list embedding the society and
its status (`in class` / `suspended` / `withdrawn`), not a bare edge; the index derives a
`classed_by` link (→company) from the most recent entry. This keeps the load-bearing fact (status
over time) first-class rather than flattening it to a single link.

---

## 3. File & link conventions

**Hybrid record.** Hard typed edges live in **YAML frontmatter** (the index's source of truth);
the **prose body** carries narrative with soft `[[links]]` (indexed as mentions). Reified edges
with properties can only live in frontmatter.

**An edge value is either** a bare wikilink string (shorthand for `inferred`, unsourced) **or an
object** `{target, <edge-properties>, source, status, by, at, note}`.

**Provenance is on every fact** — the CSCW core (§4). The status vocabulary:

| status | meaning |
|---|---|
| `inferred` | a machine asserted it (Equasis, AIS, an algorithm) |
| `confirmed` | a human looked and agrees |
| `corrected` | a human overrode the machine |
| `disputed` | conflicting assertions, kept side by side, never silently resolved |

**Wikilink format:** `[[subvault:id|display text]]` — always the colon form, e.g.
`[[vessels:9176187|Meridian Star]]`, `[[countries:pa|Panama]]`, `[[cases:2024-panama-shell]]`,
`[[ontology:vessel-477123400]]` (the join to the live graph). An unresolved link is a TODO, not
an error (§4).

### 3.1 Worked example — a vessel record (illustrative, synthetic IDs)

```markdown
---
id: vessels/9176187              # IMO number = permanent key
schema: Vessel
name: Meridian Star
imoNumber: "9176187"
mmsi: "477123400"                # mutable — join key to the ontology, NOT the key
callSign: VRXY7
type: crude oil tanker
flag: "[[countries:pa|Panama]]"          # flag STATE
registered_in: "[[registries:panama-ma|Panama Maritime Authority]]"
ontology: "[[ontology:vessel-477123400]]"   # durable-layer link to the live graph
watchlist: true

pastNames:                        # re-identification, dated
  - name: Ocean Zephyr
    until: "2024-03"
classStatus:                      # the dark-fleet risk signal, dated
  - status: withdrawn
    society: "[[companies:imo-5412345|Global Marine Register]]"
    date: "2023-11"

ownership:                        # reified edges (FTM Ownership) — typed + dated
  - owner: "[[companies:imo-8712345|Blue Sea Shipping SA]]"
    ownershipType: registered
    percentage: 100
    start: "2019-06"
    source: equasis
  - owner: "[[people:j-marchetti|Jean Marchetti]]"
    ownershipType: ultimate         # UBO
    start: "2019-06"
    status: corrected
    by: sness
    source: "[[cases:2024-panama-shell|shell-company case]]"
operated_by: "[[companies:imo-8712345|Blue Sea Shipping SA]]"
managed_by:  "[[companies:imo-9001122|Adriatic ISM Ltd]]"
insured_by:  "[[companies:pi-westgard|Westgard P&I]]"
captained_by:
  - person: "[[people:a-novak|Anton Novak]]"
    from: "2022"
authorized_by:                    # RFMO fishing authorization
  - authority: "[[orgs:iccat|ICCAT]]"
    status: none                  # NOT authorized — the IUU flag
---

# Meridian Star (IMO 9176187)

Crude tanker, Panama-flagged since 2019. Class **withdrawn** by Global Marine Register in
Nov 2023 — uninsurable through mainstream P&I after that point. Renamed from *Ocean Zephyr*
in Mar 2024; same hull across both names. Registered owner is a Panama SA whose ultimate
beneficiary traces to [[people:j-marchetti|J. Marchetti]] per [[cases:2024-panama-shell]].

## Sources
- Equasis record (IMO 9176187), fetched 2026-07-21
- [[cases:2024-panama-shell|Panama shell-company case]]
```

Resources sit beside `index.md` in the same directory: `track-2024-03.geojson`,
`sar-chip-20240312.png`, `equasis-raw.json`.

---

## 4. The collaboration model (flexible schema + human-in-the-loop)

The vault is a **mixed-initiative / CSCW artifact**: algorithms and humans both write to the same
`.md` files; the schema bends to a messy world instead of rejecting it; a human can always open a
record and fix what the machine got wrong. (This is the founder's Orchive human-in-the-loop
thesis, and the CH14 "operator override, logged" story, applied to entities.)

1. **Schema-tolerant, never reject.** A record is *always* valid — missing keys, extra fields,
   unresolved links, a bare string where an object was expected, two conflicting operators are all
   fine. The index validates **softly**: problems become a **`data-quality` report** (warnings +
   a work queue of "what needs a human"), never blocking errors. Unknown entity/relationship
   types are allowed.
2. **Every fact can carry provenance** — `{source, status, by, at, note}` (§3). A bare value =
   "inferred, unsourced."
3. **Write-discipline — humans win, the machine never clobbers.** A generator only writes facts
   it owns (`status: inferred`, its own `source`). Anything `confirmed`/`corrected` or carrying a
   human `by:` is **read-only to the machine**. Fresh machine data that conflicts with a human
   fact is recorded as a *second assertion* → `disputed`, never an overwrite. Re-running the
   Equasis generator can flag that a source now disagrees; it cannot undo your fix.
4. **Git *is* the collaboration log.** Every human edit is a commit with authorship and history —
   the "who changed what, when, why" ledger comes free.
5. **The loop feeds the platform.** Only `confirmed`/`corrected` facts write back to the ontology
   (§6) — the live graph is enriched by **vetted** knowledge, not raw inference. The
   `data-quality` queue (gaps + disputes) is the curation backlog.

---

## 5. Governance

> **Amended 2026-07-23 (DECISIONS V10a):** the repo is **public** — reframed as a *demonstration*
> of a capability a government would operate, not a public accusation service. Public content stays
> **synthetic/illustrative**; real adverse claims about named parties stay out of the public repo
> and belong in a government-operated deployment. The "starts private" bullet below is superseded;
> the rest of the section stands.

The provenance model does most of the work — every claim structurally carries a source, a status,
and an asserter, which is exactly the hedging a sensitive claim needs. What remains:

- **~~The repo starts private.~~** *(Superseded by V10a — public demonstration; see the note above.)*
  Real, sourced, but *adverse* claims about named people/companies (UBO, IUU) stay out of the public
  repo — they belong in a government-operated deployment, not the public demo.
- **Adverse claims always carry a `source`.** No bare adverse assertion about a named real party —
  it is `inferred` with a source, or human `confirmed`/`corrected` with a source. Adverse
  "why of interest" lives in `cases/`, dated and sourced.
- **Public-record vs inference is visible by construction** — flag/IMO/registered-owner (public
  record) vs beneficial ownership / IUU suspicion (inference) are separated by `status`/`source`,
  not by tone.
- Workspace norms apply: provenance over polish; no PII beyond public maritime records.

---

## 6. Vault ↔ ontology mechanism (the durable layer)

Two directions, with strict discipline so machine inference can never launder itself into
"confirmed."

**Harvest (ontology → vault) — fills skeletons.** A generator reads `planetar-ontology`'s resolved
vessels (via its Object API; the ontology also publishes `entity.<kind>.updated` on the bus). For
each MMSI seen, it resolves the **IMO number** (AIS static data / Equasis), writes/updates
`vessels/<IMO>/index.md` with AIS-derived fields — all `status: inferred`, `source: ais|equasis` —
and stamps `ontology: [[ontology:vessel-<mmsi>]]`. Write-discipline holds: it never touches a
`confirmed`/`corrected`/human field.

**Write-back (vault → ontology) — the durable layer.** An exporter walks the vault, selects **only
`confirmed`/`corrected` facts**, and publishes them on the bus as a vault-sourced enrichment
(`entity.vessel.enriched`, keyed by MMSI) that the ontology ingests and attaches to the live
entity. `planetar-ui`'s inspector then shows real operator / UBO / watchlist / class-withdrawn /
not-ICCAT-authorized, with a dossier link.

**The payoff — durable identity across mutable IDs.** The write-back keys on **IMO** and resolves
*all* MMSIs for that hull (current + `pastNames`/`same_as` history). When a vessel goes dark and
reappears under a new MMSI, the exporter still says "this new track is the same hull as the
Meridian Star dossier." The vault is what lets re-identification survive a name/flag/MMSI change —
the CH13/CH14 thesis, sitting in a directory of markdown files.

**Loop safety:** harvest writes only `inferred`; write-back exports only human-vetted. Inference
can never round-trip into confirmation.

---

## 7. Phasing

The dependency order: fix the schema → index it → serve/generate it → close the loop. **Each phase
is its own spec→plan→build cycle; only Phase 1 is specced and built now.**

| Phase | What | Code? | Delivers |
|---|---|---|---|
| **1 — Schema + seed** | The private repo + `CLAUDE.md`, the 9 sub-vaults, a `CONVENTIONS.md`, **one fully-worked seed cluster** (a vessel linked to its flag, registry, operator, UBO, cargo, port, a `case`, an RFMO), the governance/DECISIONS record | **None** (markdown only, like planetar-grants) | A browsable, traversable hyperweb that proves the schema against messy reality, and the conventions the indexer targets |
| **2 — Index** | A builder that scans the vault → SQLite (entities + reified edges + status/source) and emits the **data-quality report**. Fork the doi.bio indexer core | Yes | `planetar-vaults index` → queryable graph + work queue |
| **3 — MCP + harvest** | MCP server (fork doibio-mcp: `get_entity`/`get_related`/`find_connections`/path); the harvest generator from the ontology (§6) | Yes | Vault fills broad-and-shallow from live data; Claude traverses it as a tool |
| **4 — Write-back** | The exporter → bus `entity.vessel.enriched` → ontology → UI inspector; re-ID across an MMSI change (§6) | Yes | The loop closes; authored knowledge makes the live graph smarter |
| **5 — Other legs** *(later, optional)* | Platform self-model / design-memory / world-knowledge sub-vaults, if still wanted | — | Deferred |

**Why Phase 1 is markdown-only, content-first:** the doi.bio lesson is that the convention and a
real worked example must exist *before* any indexer — you cannot parse a schema you have not
stress-tested against a messy real entity. Phase 1 makes the hyperweb hand-traversable; everything
after is machinery pointed at a proven target.

### 7.1 Phase 1 scope (the spec that gets a plan next)

- `git init` repo (done), `.gitignore`, private.
- `CLAUDE.md` — repo-specific guidance (what this is, the conventions, the 9 sub-vaults, the
  provenance/status rules, patent/date/framing norms inherited from the workspace).
- `docs/CONVENTIONS.md` — the frontmatter schema, edge reification, status/provenance vocabulary,
  ID keying, wikilink format, resource-file conventions (a normative version of §2–§4).
- The nine sub-vault directories, each with a short `README.md` stating what it holds and its key.
- **One fully-worked seed cluster** exercising every edge type and the provenance/status states:
  a vessel + its flag country + registry + operator company + parent company + UBO person +
  captain + cargo + home/destination port + one `case` + one RFMO org. Illustrative/synthetic
  where a real adverse claim would otherwise be needed (per §5).
- `DECISIONS.md` — seeded with the decisions in this doc (entity model, FTM alignment, IMO keying,
  registries-as-type, ownership-reification, private-repo, durable-layer coupling).
- `README.md` — status dashboard pointing to this design + CONVENTIONS.

### 7.2 Non-goals (YAGNI)

- Not a runtime service in Phase 1 (no index, no MCP, no generators — those are Phases 2–4).
- Not a public dataset (private; publication is a later explicit decision).
- Not a replacement for `planetar-ontology` — it is its durable complement.
- Behaviours (AIS gaps, STS transfers, spoofing) are **evidence inside `cases/`**, not top-level
  entity types.
- No ingestion of OpenSanctions/Aleph data in Phase 1 — the FTM alignment just keeps that door
  open.

---

## 8. Open questions (to resolve during Phase 1 or later)

- Exact `CLAUDE.md` git-management story: single repo with plain sub-dirs (like planetar-grants) is
  assumed; revisit only if a sub-vault ever needs independent history.
- Whether `orgs/` should also hold flag administrations and classification-society *bodies* as it
  grows, or keep those as role-tagged `companies/`. Start with role-tagged companies; promote only
  if the query pattern demands it.
- The precise `entity.vessel.enriched` envelope shape (Phase 4, against the real ontology API).
