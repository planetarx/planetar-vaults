# planetar-vaults Phase 1 (Schema + Seed) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish the planetar-vaults maritime-entity hyperweb as a browsable, internally-consistent set of markdown conventions plus one fully-worked seed cluster — no code — that proves the schema against a messy real entity and gives the Phase-2 indexer a fixed target.

**Architecture:** Nine sub-vault directories of dir-per-entity records (`<subvault>/<id>/index.md` + resources). Hard typed edges live in YAML frontmatter; prose bodies carry narrative with `[[subvault:id|display]]` wikilinks. Every fact may carry `{source, status, by, at, note}` provenance. The schema is tolerant (never rejects); unresolved links are TODOs, not errors.

**Tech Stack:** Markdown + YAML frontmatter only. No build, no dependencies, no runtime. Verification uses `python3` (stdlib `yaml` via PyYAML if present, else a tolerant check) and shell.

## Global Constraints

- **Repo is private.** Do not add a public remote or push publicly in Phase 1. (DESIGN §5)
- **Real vs synthetic split (governance).** Public real entities that carry no adverse claim — countries, registries, ports, cargo, RFMOs — are **real**. Vessels, companies, people, and cases (which carry adverse implications like UBO / IUU) are **synthetic and clearly labelled** in Phase 1. (DESIGN §5, §7.1)
- **Wikilink form is always the colon form:** `[[subvault:id|display]]`. (DESIGN §3)
- **Entity keys align to authoritative registers:** vessels = IMO (7 digits); companies = `imo-NNNNNNN` else slug; countries = ISO-2; ports = UN/LOCODE; registries/cargo/people/orgs = slug; cases = `YYYY-slug`. (DESIGN §2)
- **Status vocabulary:** `inferred` (machine) · `confirmed` (human agrees) · `corrected` (human overrode) · `disputed` (conflicting, kept side by side). A bare value = `inferred`, unsourced. (DESIGN §3, §4)
- **FollowTheMoney naming** where it maps: `schema: Vessel|Company|Person`, `imoNumber`, `mmsi`, `callSign`, `flag`, `pastNames`, `ownership`/`ownershipType`. (DESIGN §2.2)
- **Dates absolute** (`2026-07-22`), patent framing "applicant-named inventor on US Patent 10,936,582" if ever referenced — inherited workspace norms.
- **No code in Phase 1.** Verification shell/py snippets are checks run at author time, not committed deliverables.

---

## File Structure

Created in this phase (all under `~/github/planetarx/planetar-vaults/`):

```
CLAUDE.md                        # Task 2 — repo guidance for Claude
DECISIONS.md                     # Task 5 — the decision record
docs/CONVENTIONS.md              # Task 1 — normative on-disk conventions
vessels/README.md                # Task 3
companies/README.md              # Task 3
people/README.md                 # Task 3
countries/README.md              # Task 3
registries/README.md             # Task 3
cargo/README.md                  # Task 3
ports/README.md                  # Task 3
cases/README.md                  # Task 3
orgs/README.md                   # Task 3
# seed cluster — Task 4
vessels/9990001/index.md         # MV Kestrel Dawn (synthetic hub)
vessels/9990002/index.md         # MV Kestrel Dusk (synthetic sister)
countries/pa/index.md            # Panama (real)
registries/panama-ma/index.md    # Panama Maritime Authority (real)
ports/sgsin/index.md             # Singapore (real)
cargo/crude-oil/index.md         # crude oil (real)
orgs/iccat/index.md              # ICCAT (real)
companies/blue-harbour-shipping/index.md   # operator (synthetic)
companies/kestrel-holdings/index.md        # parent (synthetic)
companies/meridian-pi/index.md             # P&I club (synthetic)
companies/atlas-class-register/index.md    # class society (synthetic)
people/alex-rivera/index.md                # UBO (synthetic)
people/jordan-blake/index.md               # captain (synthetic)
cases/2026-kestrel-shell-structure/index.md  # case (synthetic)
README.md                        # Task 5 — update status (already exists from spec commit)
```

Already present (from the design commit `18a9835`): `README.md`, `.gitignore`, `docs/DESIGN.md`.

---

### Task 1: The normative conventions doc (`docs/CONVENTIONS.md`)

Everything downstream targets this. It is the on-disk, normative version of DESIGN §2–§4 that an author (human or machine) follows without reading the whole design.

**Files:**
- Create: `docs/CONVENTIONS.md`

**Interfaces:**
- Produces: the canonical frontmatter schema, edge-object shape, status vocabulary, wikilink form, ID rules, and resource-file rules that Tasks 2–5 rely on verbatim.

- [ ] **Step 1: Write `docs/CONVENTIONS.md`** with this exact content:

````markdown
# planetar-vaults conventions (normative)

The on-disk contract every record follows. Rationale is in [`DESIGN.md`](DESIGN.md); this file is
the rules. The schema is **tolerant**: a record is always valid; problems are data-quality
warnings, never errors. Unknown fields, missing fields, and unresolved links are all allowed.

## Record layout

- One entity = one directory `<subvault>/<id>/` with a main `index.md` plus optional resources
  (`*.geojson`, `*.png`, `*.json`, …) in the same directory.
- `index.md` = YAML frontmatter (hard typed edges, machine-read) + prose body (narrative with soft
  `[[links]]`, read as mentions).

## Identifiers & keys

| Sub-vault | Key |
|---|---|
| `vessels/` | IMO number, 7 digits (permanent) |
| `companies/` | `imo-NNNNNNN` (IMO company & registered-owner number) else a slug |
| `people/` | slug (`first-last`) |
| `countries/` | ISO 3166-1 alpha-2, lowercase |
| `registries/` | slug |
| `cargo/` | slug |
| `ports/` | UN/LOCODE, lowercase (`sgsin`) |
| `cases/` | `YYYY-slug` |
| `orgs/` | slug |

`id:` in frontmatter mirrors the path: `vessels/9990001`.

## Wikilinks

Always `[[subvault:id|display text]]` (colon form). Examples:
`[[vessels:9990001|MV Kestrel Dawn]]`, `[[countries:pa|Panama]]`, `[[cases:2026-kestrel-shell-structure]]`,
`[[ontology:vessel-999000001]]` (join to the live graph). An unresolved link is a TODO, not an error.

## Provenance on every fact

A field or edge is either a **bare value** (shorthand for `inferred`, unsourced) **or an object**:

```yaml
operated_by:
  target: "[[companies:blue-harbour-shipping|Blue Harbour Shipping SA]]"
  status: corrected        # inferred | confirmed | corrected | disputed
  by: sness
  at: "2026-07-22"
  source: "[[cases:2026-kestrel-shell-structure]]"
  note: "Equasis operator stale; confirmed via port-state record"
```

- `inferred` — a machine asserted it. `confirmed` — a human agrees. `corrected` — a human overrode
  the machine. `disputed` — conflicting assertions kept side by side (a list; never silently resolved).
- **Adverse claims about a named real party always carry a `source`.** (There are none in Phase 1
  because such entities are synthetic.)

## Edge vocabulary

`flagged_under`→country · `registered_in`→registry · `on_behalf_of` (registry→country) ·
`operated_by`/`owned_by`/`managed_by`/`insured_by`→company · `beneficially_owned_by`→company|person ·
`captained_by`→person · `carries`→cargo · `home_port`/`bound_for`→port · `authorized_by`→org
(with `status` + dates) · `pastNames` (list, dated) · `same_as`/`formerly`→vessel (carry the changed
attribute + date) · `sister_of`→vessel · `parent_of`/`subsidiary_of` (company→company) ·
`officer_of` (person→company) · `involves` (case→any).

### Reified ownership

Ownership is a frontmatter list, each entry a reified edge (FollowTheMoney `Ownership`):

```yaml
ownership:
  - owner: "[[companies:blue-harbour-shipping|Blue Harbour Shipping SA]]"
    ownershipType: registered   # registered | beneficial | ultimate | direct | indirect
    percentage: 100
    start: "2019-06"
    source: equasis
```

### Class status

Class is the vessel's `classStatus` (a dated list embedding the society + status), not a bare edge;
the index derives `classed_by` from the most recent entry:

```yaml
classStatus:
  - status: withdrawn         # in-class | suspended | withdrawn
    society: "[[companies:atlas-class-register|Atlas Class Register]]"
    date: "2023-11"
```

## The ontology join

`vessels/*` carry `mmsi:` (the join key to the live graph, mutable) and
`ontology: "[[ontology:vessel-<mmsi>]]"`. The permanent bridge across MMSI changes is the IMO key
plus `pastNames`/`same_as`.

## Synthetic labelling (Phase 1)

Synthetic vessels/companies/people/cases carry `synthetic: true` in frontmatter and a one-line
italic caveat at the top of the body. Real public entities (countries, registries, ports, cargo,
orgs) do not.
````

- [ ] **Step 2: Verify the frontmatter examples parse as YAML**

Run:
```bash
cd ~/github/planetarx/planetar-vaults
python3 - <<'PY'
import re, yaml
txt = open('docs/CONVENTIONS.md').read()
blocks = re.findall(r'```yaml\n(.*?)```', txt, re.S)
for i,b in enumerate(blocks):
    yaml.safe_load(b); print(f"yaml block {i+1}: OK")
PY
```
Expected: each yaml block prints `OK` (no exception). If PyYAML is absent: `pip install pyyaml` or skip — the blocks are hand-verified valid.

- [ ] **Step 3: Commit**

```bash
git add docs/CONVENTIONS.md
git commit -m "Phase 1: normative on-disk conventions doc"
```

---

### Task 2: Repo guidance (`CLAUDE.md`)

The AI-guidance layer, in the workspace house style (see `../planetar-grants/CLAUDE.md`).

**Files:**
- Create: `CLAUDE.md`

**Interfaces:**
- Consumes: the conventions from Task 1 (references them, does not restate the schema).

- [ ] **Step 1: Write `CLAUDE.md`** with this exact content:

````markdown
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
`../planetar-grants`). Commit here. **The repo is private** — do not add a public remote (governance:
it holds sourced-but-adverse claims about named parties; Phase-1 such entities are synthetic).

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
````

- [ ] **Step 2: Verify links point at files that exist**

Run:
```bash
cd ~/github/planetarx/planetar-vaults
for f in docs/DESIGN.md docs/CONVENTIONS.md; do test -f "$f" && echo "ok: $f" || echo "MISSING: $f"; done
```
Expected: both `ok:`.

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "Phase 1: repo CLAUDE.md guidance"
```

---

### Task 3: The nine sub-vault directories + READMEs

Creates the skeleton. Each README is one small file from a shared template with per-sub-vault values.

**Files:**
- Create: `vessels/README.md`, `companies/README.md`, `people/README.md`, `countries/README.md`, `registries/README.md`, `cargo/README.md`, `ports/README.md`, `cases/README.md`, `orgs/README.md`

**Interfaces:**
- Produces: the nine directories the seed cluster (Task 4) writes into.

- [ ] **Step 1: Create each README** using this template — substitute `{ENTITY}`, `{KEY}`, `{HOLDS}`, `{REAL}` from the table below:

Template:
```markdown
# {ENTITY}

Sub-vault of [planetar-vaults](../README.md). One directory per entity: `{KEY-EXAMPLE}/index.md`.

- **Holds:** {HOLDS}
- **Key:** {KEY}
- **Phase 1 data:** {REAL}

See [`../docs/CONVENTIONS.md`](../docs/CONVENTIONS.md) for the record format.
```

Per-sub-vault values:

| File | {ENTITY} | {KEY} | {KEY-EXAMPLE} | {HOLDS} | {REAL} |
|---|---|---|---|---|---|
| `vessels/README.md` | Vessels | IMO number (7 digits, permanent) | `vessels/9990001` | ships; the hub of the graph | synthetic (`synthetic: true`) |
| `companies/README.md` | Companies | `imo-NNNNNNN` else slug | `companies/blue-harbour-shipping` | operators, owners, managers, parents, class societies (role), P&I clubs (role) | synthetic |
| `people/README.md` | People | slug (`first-last`) | `people/alex-rivera` | captains, owners, UBOs, officers | synthetic |
| `countries/README.md` | Countries | ISO 3166-1 alpha-2 (lowercase) | `countries/pa` | flag states | real |
| `registries/README.md` | Registries | slug | `registries/panama-ma` | the registering body (distinct from the flag state); open/second/fraudulent registries | real |
| `cargo/README.md` | Cargo | slug | `cargo/crude-oil` | commodities and specific cargoes | real |
| `ports/README.md` | Ports | UN/LOCODE (lowercase) | `ports/sgsin` | registry / call / destination ports | real |
| `cases/README.md` | Cases | `YYYY-slug` | `cases/2026-kestrel-shell-structure` | dark-vessel events, detentions, IUU incidents; where "why of interest" lives | synthetic |
| `orgs/README.md` | Organizations & authorities | slug | `orgs/iccat` | RFMOs and authorities (targets of `authorized_by`) | real |

- [ ] **Step 2: Verify all nine exist**

Run:
```bash
cd ~/github/planetarx/planetar-vaults
n=$(ls vessels/README.md companies/README.md people/README.md countries/README.md registries/README.md cargo/README.md ports/README.md cases/README.md orgs/README.md 2>/dev/null | wc -l)
echo "$n/9 sub-vault READMEs present"
```
Expected: `9/9 sub-vault READMEs present`.

- [ ] **Step 3: Commit**

```bash
git add vessels companies people countries registries cargo ports cases orgs
git commit -m "Phase 1: nine sub-vault directories + READMEs"
```

---

### Task 4: The seed cluster

One fully-worked, internally-consistent synthetic cluster that exercises **every edge type and every provenance status**. Build the spokes first (they may link to the vessel before it exists — allowed), then the hub, then the second vessel, then verify the whole graph resolves.

**Files (all `index.md`):**
- Create: `countries/pa/`, `registries/panama-ma/`, `ports/sgsin/`, `cargo/crude-oil/`, `orgs/iccat/`, `companies/blue-harbour-shipping/`, `companies/kestrel-holdings/`, `companies/meridian-pi/`, `companies/atlas-class-register/`, `people/alex-rivera/`, `people/jordan-blake/`, `cases/2026-kestrel-shell-structure/`, `vessels/9990001/`, `vessels/9990002/`

**Interfaces:**
- Consumes: conventions (Task 1), directories (Task 3).
- Produces: a traversable graph; **coverage targets** — every edge type in the CONVENTIONS vocabulary appears at least once, and all four statuses (`inferred`, `confirmed`, `corrected`, `disputed`) appear.

- [ ] **Step 1: Real spokes — `countries/pa/index.md`**

```markdown
---
id: countries/pa
schema: Country
name: Panama
iso2: pa
---

# Panama

Flag state; operates a large open registry via the [[registries:panama-ma|Panama Maritime Authority]].
```

- [ ] **Step 2: Real spoke — `registries/panama-ma/index.md`**

```markdown
---
id: registries/panama-ma
schema: Registry
name: Panama Maritime Authority
on_behalf_of: "[[countries:pa|Panama]]"
registry_type: open
---

# Panama Maritime Authority

The registering body for the Panamanian open registry. A legitimate registry (contrast: fraudulent
registries link to no country).
```

- [ ] **Step 3: Real spokes — `ports/sgsin/index.md`, `cargo/crude-oil/index.md`, `orgs/iccat/index.md`**

`ports/sgsin/index.md`:
```markdown
---
id: ports/sgsin
schema: Port
name: Singapore
unlocode: SGSIN
country: "[[countries:sg|Singapore]]"
---

# Singapore (SGSIN)

Major bunkering and transhipment port. (Its `country` link to `[[countries:sg]]` is unresolved in
Phase 1 — a TODO, not an error.)
```

`cargo/crude-oil/index.md`:
```markdown
---
id: cargo/crude-oil
schema: Cargo
name: Crude oil
---

# Crude oil

Unrefined petroleum; a primary tanker commodity.
```

`orgs/iccat/index.md`:
```markdown
---
id: orgs/iccat
schema: Org
name: International Commission for the Conservation of Atlantic Tunas
short: ICCAT
org_type: RFMO
---

# ICCAT

Regional Fisheries Management Organization for Atlantic tunas. Issues fishing authorizations; a
vessel operating without one where required is an IUU signal (`authorized_by … status: none`).
```

- [ ] **Step 4: Synthetic companies — the four `companies/*/index.md`**

`companies/blue-harbour-shipping/index.md`:
```markdown
---
id: companies/blue-harbour-shipping
schema: Company
name: Blue Harbour Shipping SA
synthetic: true
roles: [operator, registered-owner, manager]
subsidiary_of: "[[companies:kestrel-holdings|Kestrel Holdings Ltd]]"
---

*Synthetic — illustrative, not a real company.*

# Blue Harbour Shipping SA

Operator and registered owner of record for [[vessels:9990001|MV Kestrel Dawn]] and its sister
[[vessels:9990002|MV Kestrel Dusk]]. A subsidiary of [[companies:kestrel-holdings|Kestrel Holdings]].
```

`companies/kestrel-holdings/index.md`:
```markdown
---
id: companies/kestrel-holdings
schema: Company
name: Kestrel Holdings Ltd
synthetic: true
parent_of: "[[companies:blue-harbour-shipping|Blue Harbour Shipping SA]]"
---

*Synthetic — illustrative, not a real company.*

# Kestrel Holdings Ltd

Parent of [[companies:blue-harbour-shipping|Blue Harbour Shipping]]. Ultimate beneficiary is
[[people:alex-rivera|Alex Rivera]] (see [[cases:2026-kestrel-shell-structure]]).
```

`companies/meridian-pi/index.md`:
```markdown
---
id: companies/meridian-pi
schema: Company
name: Meridian P&I (synthetic)
synthetic: true
roles: [insurer]
---

*Synthetic — illustrative, not a real P&I club.*

# Meridian P&I

Protection & indemnity cover for [[vessels:9990001|MV Kestrel Dawn]] until class withdrawal
(loss of class → loss of mainstream P&I).
```

`companies/atlas-class-register/index.md`:
```markdown
---
id: companies/atlas-class-register
schema: Company
name: Atlas Class Register (synthetic)
synthetic: true
roles: [classification-society]
---

*Synthetic — illustrative, not a real classification society.*

# Atlas Class Register

Classification society that **withdrew** class from [[vessels:9990001|MV Kestrel Dawn]] in 2023-11.
```

- [ ] **Step 5: Synthetic people — `people/alex-rivera/index.md`, `people/jordan-blake/index.md`**

`people/alex-rivera/index.md`:
```markdown
---
id: people/alex-rivera
schema: Person
name: Alex Rivera
synthetic: true
officer_of: "[[companies:kestrel-holdings|Kestrel Holdings Ltd]]"
---

*Synthetic — illustrative, not a real person.*

# Alex Rivera

Officer of [[companies:kestrel-holdings|Kestrel Holdings]]; asserted ultimate beneficial owner of
[[vessels:9990001|MV Kestrel Dawn]] per [[cases:2026-kestrel-shell-structure]].
```

`people/jordan-blake/index.md`:
```markdown
---
id: people/jordan-blake
schema: Person
name: Jordan Blake
synthetic: true
---

*Synthetic — illustrative, not a real person.*

# Jordan Blake

Master of [[vessels:9990001|MV Kestrel Dawn]] since 2022.
```

- [ ] **Step 6: Synthetic case — `cases/2026-kestrel-shell-structure/index.md`**

```markdown
---
id: cases/2026-kestrel-shell-structure
schema: Case
name: Kestrel shell-company structure
synthetic: true
date: "2026-05"
involves:
  - "[[vessels:9990001|MV Kestrel Dawn]]"
  - "[[companies:blue-harbour-shipping|Blue Harbour Shipping SA]]"
  - "[[companies:kestrel-holdings|Kestrel Holdings Ltd]]"
  - "[[people:alex-rivera|Alex Rivera]]"
---

*Synthetic — illustrative; no real-world claim.*

# Kestrel shell-company structure (2026-05)

Illustrative case tying the registered owner ([[companies:blue-harbour-shipping|Blue Harbour]]) to a
parent ([[companies:kestrel-holdings|Kestrel Holdings]]) and an ultimate beneficiary
([[people:alex-rivera|Alex Rivera]]). Demonstrates that "why of interest" is a dated, sourced case
record linking parties — not a bare adverse attribute on the person.

## Sources
- Synthetic scenario authored 2026-07-22 to exercise the schema.
```

- [ ] **Step 7: The hub — `vessels/9990001/index.md`** (exercises the remaining edges + all statuses)

```markdown
---
id: vessels/9990001
schema: Vessel
name: MV Kestrel Dawn
synthetic: true
imoNumber: "9990001"
mmsi: "999000001"
callSign: TEST1
type: crude oil tanker
ontology: "[[ontology:vessel-999000001]]"
watchlist: true

flag: "[[countries:pa|Panama]]"
registered_in: "[[registries:panama-ma|Panama Maritime Authority]]"
home_port: "[[ports:sgsin|Singapore]]"
bound_for: "[[ports:sgsin|Singapore]]"
carries: "[[cargo:crude-oil|Crude oil]]"
sister_of: "[[vessels:9990002|MV Kestrel Dusk]]"

pastNames:
  - name: MV Harbour Zephyr
    until: "2024-03"

classStatus:
  - status: withdrawn
    society: "[[companies:atlas-class-register|Atlas Class Register]]"
    date: "2023-11"

operated_by:
  target: "[[companies:blue-harbour-shipping|Blue Harbour Shipping SA]]"
  status: confirmed
  by: sness
  at: "2026-07-22"
  source: equasis
managed_by: "[[companies:blue-harbour-shipping|Blue Harbour Shipping SA]]"
insured_by: "[[companies:meridian-pi|Meridian P&I]]"

ownership:
  - owner: "[[companies:blue-harbour-shipping|Blue Harbour Shipping SA]]"
    ownershipType: registered
    percentage: 100
    start: "2019-06"
    source: equasis
  - owner: "[[people:alex-rivera|Alex Rivera]]"
    ownershipType: ultimate
    start: "2019-06"
    status: corrected
    by: sness
    at: "2026-07-22"
    source: "[[cases:2026-kestrel-shell-structure]]"
    note: "Registry names only the SA; UBO established via the case."

managed_by_disputed:            # illustrates the `disputed` status: two conflicting assertions
  - target: "[[companies:blue-harbour-shipping|Blue Harbour Shipping SA]]"
    status: disputed
    source: equasis
  - target: "[[companies:kestrel-holdings|Kestrel Holdings Ltd]]"
    status: disputed
    source: "[[cases:2026-kestrel-shell-structure]]"
    note: "Case suggests day-to-day management sits with the parent; unresolved."

captained_by:
  - person: "[[people:jordan-blake|Jordan Blake]]"
    from: "2022"

authorized_by:
  - authority: "[[orgs:iccat|ICCAT]]"
    status: none
---

*Synthetic — illustrative, not a real vessel.*

# MV Kestrel Dawn (IMO 9990001)

Crude tanker, Panama-flagged since 2019, registered by the
[[registries:panama-ma|Panama Maritime Authority]]. Class **withdrawn** by
[[companies:atlas-class-register|Atlas Class Register]] in 2023-11 — uninsurable through mainstream
P&I after that point. Renamed from *MV Harbour Zephyr* in 2024-03; same hull across both names.
Sister of [[vessels:9990002|MV Kestrel Dusk]]. Registered owner
[[companies:blue-harbour-shipping|Blue Harbour Shipping SA]]; ultimate beneficiary
[[people:alex-rivera|Alex Rivera]] per [[cases:2026-kestrel-shell-structure]]. Not authorized by
[[orgs:iccat|ICCAT]].

## Sources
- Synthetic scenario authored 2026-07-22 to exercise the schema.
```

- [ ] **Step 8: The sister — `vessels/9990002/index.md`** (minimal; gives the operator a fleet-of-two)

```markdown
---
id: vessels/9990002
schema: Vessel
name: MV Kestrel Dusk
synthetic: true
imoNumber: "9990002"
mmsi: "999000002"
type: crude oil tanker
flag: "[[countries:pa|Panama]]"
operated_by: "[[companies:blue-harbour-shipping|Blue Harbour Shipping SA]]"
sister_of: "[[vessels:9990001|MV Kestrel Dawn]]"
---

*Synthetic — illustrative, not a real vessel.*

# MV Kestrel Dusk (IMO 9990002)

Sister of [[vessels:9990001|MV Kestrel Dawn]], same operator
[[companies:blue-harbour-shipping|Blue Harbour Shipping]]. Present so the
"operator → its fleet" traversal is real.
```

- [ ] **Step 9: Verify every `index.md` frontmatter parses as YAML**

Run:
```bash
cd ~/github/planetarx/planetar-vaults
python3 - <<'PY'
import glob, yaml, sys
bad=0
for f in glob.glob('*/*/index.md'):
    fm = open(f).read().split('---',2)
    try: yaml.safe_load(fm[1]); print("ok:", f)
    except Exception as e: bad+=1; print("FAIL:", f, e)
sys.exit(1 if bad else 0)
PY
```
Expected: every file prints `ok:`, exit 0.

- [ ] **Step 10: Verify every wikilink resolves to a file that exists** (the seed must be internally complete; `ontology:`, `countries:sg` are the only allowed unresolved links)

Run:
```bash
cd ~/github/planetarx/planetar-vaults
python3 - <<'PY'
import glob, re
targets=set()
for f in glob.glob('*/*/index.md'):
    for sv,idv in re.findall(r'\[\[([a-z-]+):([a-z0-9/-]+?)(?:\|[^\]]*)?\]\]', open(f).read()):
        targets.add((sv,idv))
allow={'ontology'}          # external join namespace
missing=[]
for sv,idv in sorted(targets):
    if sv in allow: continue
    import os
    if not os.path.exists(f"{sv}/{idv}/index.md"): missing.append(f"{sv}:{idv}")
print("unresolved (expected only countries:sg):", missing)
PY
```
Expected: `unresolved (expected only countries:sg): ['countries:sg']` — i.e. the deliberate Singapore-country TODO and nothing else.

- [ ] **Step 11: Verify edge-type and status coverage**

Run:
```bash
cd ~/github/planetarx/planetar-vaults
echo "-- statuses present (want all 4) --"
grep -rhoE "status: (inferred|confirmed|corrected|disputed)" */*/index.md | sort -u
echo "-- key edges present --"
for e in flagged_under registered_in on_behalf_of operated_by managed_by insured_by ownership captained_by carries home_port bound_for authorized_by pastNames classStatus sister_of parent_of subsidiary_of officer_of involves; do
  grep -rqlE "(^|  )$e:" */*/index.md && echo "ok: $e" || echo "MISSING: $e"
done
```
Expected: `confirmed`, `corrected`, `disputed` all appear (plus bare-inferred everywhere); every edge prints `ok:`.

- [ ] **Step 12: Commit**

```bash
git add vessels companies people countries registries cargo ports cases orgs
git commit -m "Phase 1: seed cluster (synthetic Kestrel fleet) exercising every edge + status"
```

---

### Task 5: Decision record + status + final sweep

**Files:**
- Create: `DECISIONS.md`
- Modify: `README.md` (flip status to "Phase 1 landed")

**Interfaces:**
- Consumes: everything above.

- [ ] **Step 1: Write `DECISIONS.md`**

````markdown
# planetar-vaults decisions

Filed decisions from the design + Phase-1 build. Append dated updates; don't rewrite.

- **V1 (2026-07-22) Purpose.** A maritime-domain entity hyperweb; the durable knowledge layer for
  `planetar-ontology`. Modeled on the entity side of doi.bio.
- **V2 (2026-07-22) Entity model.** Nine sub-vaults: vessels, companies, people, countries,
  registries, cargo, ports, cases, orgs.
- **V3 (2026-07-22) Keying.** Vessels = IMO (permanent); companies = IMO-company-id else slug; MMSI
  is the ontology join key, never the vessel key.
- **V4 (2026-07-22) Class societies & P&I** are role-tagged companies, not their own types; class is
  the vessel's dated `classStatus`.
- **V5 (2026-07-22) Registries** are their own type, distinct from countries (fraudulent registries
  have no legitimate country parent).
- **V6 (2026-07-22) Ownership is reified** (FollowTheMoney): `ownershipType`/`percentage`/dates on
  each edge; no "network" entity.
- **V7 (2026-07-22) Vocabulary** aligns to FollowTheMoney where it maps.
- **V8 (2026-07-22) Collaboration model.** Schema-tolerant; per-fact provenance/status; the machine
  never clobbers a human; git is the collaboration log.
- **V9 (2026-07-22) Vault ↔ ontology.** The vault is the durable layer: harvest (`inferred`
  skeletons) + write-back (`confirmed`/`corrected` facts to the live graph).
- **V10 (2026-07-22) Governance.** Repo private to start; adverse claims about named real parties
  always sourced and confined to `cases/`; Phase-1 such entities are synthetic. Publication is a
  later explicit decision.
- **V11 (2026-07-22) Phasing.** 1 = schema + seed (markdown only); 2 = index; 3 = MCP + harvest;
  4 = write-back; 5 = other legs (deferred).
````

- [ ] **Step 2: Update `README.md`** — replace the "What's here now" table row and status line:

Change the status callout to:
```markdown
> **Status: Phase 1 LANDED 2026-07-22 — schema + seed, markdown only.** Read
> [`docs/DESIGN.md`](docs/DESIGN.md) and [`docs/CONVENTIONS.md`](docs/CONVENTIONS.md). Private repo.
```
And add rows to the table for `docs/CONVENTIONS.md`, `CLAUDE.md`, the nine sub-vaults, the seed cluster, `DECISIONS.md`.

- [ ] **Step 3: Final consistency sweep** (re-run the Task 4 verifications across the whole repo)

Run:
```bash
cd ~/github/planetarx/planetar-vaults
python3 - <<'PY'
import glob, yaml
for f in glob.glob('**/index.md', recursive=True):
    yaml.safe_load(open(f).read().split('---',2)[1])
print("all frontmatter parses")
PY
grep -rq "synthetic: true" vessels companies people cases && echo "synthetic labels present"
```
Expected: `all frontmatter parses` and `synthetic labels present`.

- [ ] **Step 4: Commit**

```bash
git add DECISIONS.md README.md
git commit -m "Phase 1: decision record + status; Phase 1 complete"
```

---

## Self-Review

**Spec coverage** (DESIGN.md → task):
- §1 what it is / §1.1 relationships → CLAUDE.md (Task 2), README.
- §2 entity model / §2.1 three decisions / §2.2 FTM / §2.3 edges → CONVENTIONS (Task 1), seed exercises all (Task 4), DECISIONS V2–V7 (Task 5).
- §3 file/link conventions → CONVENTIONS (Task 1), worked in the seed (Task 4).
- §4 collaboration model (status, provenance, write-discipline) → CONVENTIONS (Task 1), all four statuses in the seed (Task 4 Step 11), DECISIONS V8.
- §5 governance (private, real/synthetic, cases-not-attributes) → Global Constraints, CLAUDE.md, synthetic labels + `cases/` in seed, DECISIONS V10.
- §6 vault↔ontology → documented in CONVENTIONS (the `ontology:` join) + DESIGN; **mechanism is Phase 3–4, correctly out of Phase-1 scope.**
- §7 phasing / §7.1 Phase-1 scope → this whole plan; §7.2 non-goals honored (no code). DECISIONS V11.
- §8 open questions → left open, not forced (correct).

**Placeholder scan:** no TBD/TODO in deliverable content (the word "TODO" appears only as the *defined term* for unresolved links). All file contents are complete.

**Type/name consistency:** ids, slugs, and wikilink targets are consistent across tasks (`vessels:9990001`, `companies:blue-harbour-shipping`, `people:alex-rivera`, `cases:2026-kestrel-shell-structure`, `orgs:iccat` used identically everywhere). Edge names match the CONVENTIONS vocabulary. The only intentional unresolved link is `countries:sg` (Task 4 Step 10 asserts exactly this).

**Scope:** single subsystem (the vault's schema + seed), markdown only, one plan. Correct.
