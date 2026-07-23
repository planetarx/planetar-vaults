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

`flag`→country (FollowTheMoney key for the *flagged-under* relationship) · `registered_in`→registry · `on_behalf_of` (registry→country) ·
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
