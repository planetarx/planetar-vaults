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

insured_by: "[[companies:meridian-pi|Meridian P&I]]"

managed_by:
  - target: "[[companies:blue-harbour-shipping|Blue Harbour Shipping SA]]"
    status: disputed
    source: equasis
  - target: "[[companies:kestrel-holdings|Kestrel Holdings Ltd]]"
    status: disputed
    source: "[[cases:2026-kestrel-shell-structure]]"
    note: "Case suggests day-to-day management sits with the parent; unresolved."

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
