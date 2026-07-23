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
- **V7 (2026-07-22) Vocabulary** aligns to FollowTheMoney where it maps. Reconciled during the
  Phase-1 build: the flag-state edge key is `flag` (FTM), not `flagged_under`.
- **V8 (2026-07-22) Collaboration model.** Schema-tolerant; per-fact provenance/status; the machine
  never clobbers a human; git is the collaboration log.
- **V9 (2026-07-22) Vault ↔ ontology.** The vault is the durable layer: harvest (`inferred`
  skeletons) + write-back (`confirmed`/`corrected` facts to the live graph).
- **V10 (2026-07-22) Governance.** Repo private to start; adverse claims about named real parties
  always sourced and confined to `cases/`; Phase-1 such entities are synthetic. Publication is a
  later explicit decision.
  - **V10a (2026-07-23) — amended: the repo is PUBLIC.** Reframed: this repo is a **public
    demonstration** of a capability a government would operate — not a public accusation service.
    The public artifact holds **synthetic/illustrative** entities and the schema/methodology
    (like OpenSanctions / OCCRP Aleph / Global Fishing Watch, which are public). **Real adverse
    claims about named real parties stay OUT of the public repo** — they belong in a
    government-operated deployment. If any *real* facts are ever added to the public demo, they
    must be public-record / official / externally-reported and sourced+hedged via `status`/`source`/
    `cases` — never a self-originated accusation about a private individual. A real legal review is
    the one worthwhile precaution before any real person lands in a public deployment.
- **V11 (2026-07-22) Phasing.** 1 = schema + seed (markdown only); 2 = index; 3 = MCP + harvest;
  4 = write-back; 5 = other legs (deferred).
