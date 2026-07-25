#!/usr/bin/env python3
"""planetar-vaults index builder (Phase 2).

Scans the vault's `<subvault>/<id>/index.md` records, parses YAML frontmatter
(hard typed edges) and body wikilinks (soft mentions), and builds a SQLite
index (entities + reified edges + mentions). Then emits a data-quality report:
unresolved links, disputed facts, orphans, and recommended-field gaps.

Schema-tolerant by design (DESIGN §4): nothing here rejects a record — problems
become warnings in the report, never errors. Unresolved links are TODOs.

Usage:  python3 tools/index.py [--db index.db] [--report data-quality.md]
Deps:   stdlib sqlite3 + PyYAML.
"""
import argparse
import glob
import os
import re
import sqlite3
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required: pip install pyyaml")

WIKILINK = re.compile(r"\[\[([a-z-]+):([a-z0-9/_-]+?)(?:\|[^\]]*)?\]\]")
# Namespaces that live outside the vault (external joins) — never "unresolved".
EXTERNAL_NS = {"ontology"}
# Frontmatter keys that are metadata, not edges.
NON_EDGE_KEYS = {"id", "schema", "name", "synthetic", "imoNumber", "mmsi",
                 "callSign", "type", "watchlist", "iso2", "unlocode", "short",
                 "org_type", "registry_type", "roles", "date"}
# Soft "recommended" fields per schema — a gap is a warning, never an error.
RECOMMENDED = {"Vessel": ["flag", "operated_by"]}


def parse_record(path):
    """Return (frontmatter dict, body str). Tolerant: bad YAML -> empty dict."""
    text = open(path, encoding="utf-8").read()
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    try:
        fm = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        fm = {}
    return (fm if isinstance(fm, dict) else {}), parts[2]


def links_in(value):
    """Yield (subvault, id) for every wikilink anywhere inside a value."""
    for sv, idv in WIKILINK.findall(str_of(value)):
        yield sv, idv


def str_of(value):
    """Flatten a frontmatter value to a string for wikilink scanning."""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return " ".join(str_of(v) for v in value.values())
    if isinstance(value, list):
        return " ".join(str_of(v) for v in value)
    return str(value)


# Dict keys that name the edge's DESTINATION (vs source/by/note = provenance).
TARGET_KEYS = ("target", "owner", "society", "authority", "person")


def link_target(value):
    """Return 'subvault/id' of the first wikilink in `value`, else None."""
    for sv, idv in links_in(value):
        return f"{sv}/{idv}"
    return None


def source_of(value):
    """The provenance source: a wikilink target if present, else the raw string."""
    if value is None:
        return None
    return link_target(value) or str(value)


def edges_from(rel, value):
    """Yield (rel, dst_id, status, source, by) from a frontmatter field.

    Handles bare wikilink strings, single objects, and lists of either — the
    polymorphism the collaboration model allows. The destination comes ONLY from
    a target-role key (or a bare link); `source`/`by`/`note` are provenance, not
    additional edges.
    """
    if isinstance(value, list):
        for item in value:
            yield from edges_from(rel, item)
        return
    if isinstance(value, dict):
        status = value.get("status", "inferred")
        source = source_of(value.get("source"))
        by = value.get("by")
        dst = next((link_target(value[k]) for k in TARGET_KEYS if k in value), None)
        if dst is None:  # dict without a named target key: scan non-provenance values
            dst = next((link_target(v) for k, v in value.items()
                        if k not in ("source", "by", "note", "status") and link_target(v)),
                       None)
        if dst:
            sv = dst.split("/", 1)[0]
            yield rel, dst, ("external" if sv in EXTERNAL_NS else status), source, by
        return
    # bare string (or scalar) — a wikilink here is the destination
    for sv, idv in links_in(value):
        yield rel, f"{sv}/{idv}", ("external" if sv in EXTERNAL_NS else "inferred"), None, None


def build(db_path):
    con = sqlite3.connect(db_path)
    con.executescript("""
        DROP TABLE IF EXISTS entities;
        DROP TABLE IF EXISTS edges;
        DROP TABLE IF EXISTS mentions;
        CREATE TABLE entities(id TEXT PRIMARY KEY, subvault TEXT, schema TEXT,
                              name TEXT, synthetic INT, path TEXT);
        CREATE TABLE edges(src TEXT, rel TEXT, dst TEXT, status TEXT,
                           source TEXT, by TEXT);
        CREATE TABLE mentions(src TEXT, dst TEXT);
    """)
    entities = {}
    for path in sorted(glob.glob("*/*/index.md")):
        subvault = path.split("/", 1)[0]
        fm, body = parse_record(path)
        eid = fm.get("id") or path.rsplit("/", 1)[0]
        entities[eid] = fm
        con.execute("INSERT OR REPLACE INTO entities VALUES(?,?,?,?,?,?)",
                    (eid, subvault, fm.get("schema"), fm.get("name"),
                     1 if fm.get("synthetic") else 0, path))
        for rel, value in fm.items():
            if rel in NON_EDGE_KEYS:
                continue
            for e in edges_from(rel, value):
                con.execute("INSERT INTO edges VALUES(?,?,?,?,?,?)", (eid, *e))
        for sv, idv in WIKILINK.findall(body):
            con.execute("INSERT INTO mentions VALUES(?,?)", (eid, f"{sv}/{idv}"))
    con.commit()
    return con, set(entities), entities


def report(con, ids, entities):
    lines = ["# planetar-vaults data-quality report", ""]
    ent_ct = con.execute("SELECT count(*) FROM entities").fetchone()[0]
    edge_ct = con.execute("SELECT count(*) FROM edges").fetchone()[0]
    lines.append(f"**{ent_ct} entities · {edge_ct} typed edges · "
                 f"{con.execute('SELECT count(*) FROM mentions').fetchone()[0]} mentions**")
    lines.append("")

    # Unresolved edges (dst not an entity; external namespaces excluded).
    rows = con.execute("SELECT src,rel,dst,status FROM edges").fetchall()
    unresolved = sorted({(s, r, d) for s, r, d, st in rows
                         if st != "external" and d not in ids})
    lines += section("Unresolved links (TODOs, not errors)", unresolved,
                     lambda x: f"`{x[0]}` --{x[1]}--> `{x[2]}` (no such record)")

    disputed = con.execute(
        "SELECT src,rel,dst FROM edges WHERE status='disputed'").fetchall()
    lines += section("Disputed facts (kept side by side)", disputed,
                     lambda x: f"`{x[0]}` --{x[1]}--> `{x[2]}`")

    # Orphans: no in/out edges and no mentions in either direction.
    linked = set()
    for s, d in con.execute("SELECT src,dst FROM edges").fetchall():
        linked.add(s); linked.add(d)
    for s, d in con.execute("SELECT src,dst FROM mentions").fetchall():
        linked.add(s); linked.add(d)
    orphans = sorted(i for i in ids if i not in linked)
    lines += section("Orphans (no edges or mentions)", orphans, lambda x: f"`{x}`")

    # Recommended-field gaps.
    gaps = []
    for eid, fm in entities.items():
        for field in RECOMMENDED.get(fm.get("schema"), []):
            if field not in fm:
                gaps.append(f"`{eid}` ({fm.get('schema')}) missing recommended `{field}`")
    lines += section("Recommended-field gaps", gaps, lambda x: x)
    return "\n".join(lines) + "\n"


def section(title, items, fmt):
    out = [f"## {title} — {len(items)}", ""]
    out += [f"- {fmt(i)}" for i in items] or ["_none_"]
    out.append("")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="index.db")
    ap.add_argument("--report", default=None,
                    help="write the data-quality report to this file (else stdout)")
    args = ap.parse_args()
    if not glob.glob("*/*/index.md"):
        sys.exit("no records found — run from the planetar-vaults repo root")
    con, ids, entities = build(args.db)
    rpt = report(con, ids, entities)
    if args.report:
        open(args.report, "w").write(rpt)
        print(f"index -> {args.db}   report -> {args.report}")
    else:
        print(rpt)


if __name__ == "__main__":
    main()
