#!/usr/bin/env python3
"""
NeuraVision Research Lab — static site generator.

Zero third-party dependencies (Python 3.8+ standard library only).

Pipeline:  data/*.csv  +  templates/*.html  ->  pre-rendered *.html (repo root)

The CSV files in data/ are the single source of truth for all content. Edit a
CSV, run `python3 build.py`, and the static pages are regenerated. The template
syntax is a small Jinja-like subset ({{ var }}, {% for %}, {% if %}, {% include %}),
so migrating to a dynamic backend (Flask/Jinja2, Eleventy, etc.) later is trivial.

Usage:
    python3 build.py            # build the site
    python3 build.py --serve    # build, then serve at http://localhost:8000
    python3 build.py --check     # build into a temp dir and report, don't write
"""
from __future__ import annotations

import csv
import html
import re
import sys
import shutil
from datetime import datetime, date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
TPL = ROOT / "templates"
OUT = ROOT  # pages are emitted into the repository root for GitHub Pages


# --------------------------------------------------------------------------- #
#  Data loading                                                               #
# --------------------------------------------------------------------------- #
def _read_rows(name: str) -> list[dict]:
    path = DATA / name
    with path.open(encoding="utf-8-sig", newline="") as f:
        return [ {k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f) ]


def _int_column(rows: list[dict], column: str, csv_name: str) -> None:
    """Parse an integer column in place, naming the row when a value is not a number.

    Row numbers count data rows, not file lines, because a quoted field may
    span several lines (publications.csv carries multi-line BibTeX).
    """
    for i, r in enumerate(rows, 1):
        try:
            r[column] = int(r[column])
        except ValueError:
            raise SystemExit(f"data/{csv_name}: row {i} has {column}={r[column]!r}, "
                             f"which is not a whole number")


def load_pages() -> list[dict]:
    rows = _read_rows("pages.csv")
    _int_column(rows, "nav_order", "pages.csv")
    rows.sort(key=lambda r: r["nav_order"])
    return rows


def load_site() -> dict:
    kv = {}
    with (DATA / "site.csv").open(encoding="utf-8-sig", newline="") as f:
        for row in csv.reader(f):
            if len(row) >= 2 and row[0] != "key":
                kv[row[0].strip()] = row[1].strip()
    # map_embed is whatever embed url site.csv holds, so the provider is a data
    # choice; the "open in map" link is derived from the same coordinates.
    lat, lng = kv["map_lat"], kv["map_lng"]
    kv["map_link"] = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
    return kv


def _split_list(value: str) -> list[str]:
    return [p.strip() for p in re.split(r"[;|]", value) if p.strip()]


def load_members() -> dict:
    rows = _read_rows("members.csv")
    _int_column(rows, "order", "members.csv")
    for r in rows:
        r["interests_list"] = _split_list(r["interests"])
        r["tag"] = r["interests_list"][0] if r["interests_list"] else ""
        r["interests_str"] = " · ".join(r["interests_list"])
        r["has_photo"] = bool(r["photo"])
        r["initials"] = "".join(w[0] for w in r["name"].split()[:2]).upper()
        r["url"] = f"{r['slug']}.html"
    rows.sort(key=lambda r: r["order"])
    pi = [r for r in rows if r["group"] == "pi"]
    students = [r for r in rows if r["group"] != "pi"]
    pi0 = pi[0] if pi else None
    return {"all": rows, "pi": pi0, "pi_list": ([pi0] if pi0 else []),
            "students": students, "student_count": len(students)}


# Letters that survive NFKD because they are distinct glyphs rather than
# accented forms. Turkish dotless i (Ozaydin) and Polish l-with-stroke
# (Gwizdala, Kozinski) both occur in the member and author names.
_FOLD_MAP = str.maketrans({"ı": "i", "ł": "l", "Ł": "L"})


def _fold(s: str) -> str:
    import unicodedata
    s = s.translate(_FOLD_MAP)
    return "".join(c for c in unicodedata.normalize("NFKD", s)
                   if not unicodedata.combining(c)).lower()


def _format_authors(authors: str, pi_surnames: set, lab_surnames: set) -> str:
    out = []
    for tok in [t.strip() for t in authors.split(",")]:
        if not tok:
            continue
        folded = _fold(tok)
        cls = None
        if any(s in folded for s in pi_surnames):
            cls = "pi"
        elif any(s in folded for s in lab_surnames):
            cls = "lab"
        esc = html.escape(tok)
        out.append(f'<span class="{cls}">{esc}</span>' if cls else esc)
    return ", ".join(out)


def load_publications(recent_count: int, pi_surnames: set, lab_surnames: set) -> dict:
    rows = _read_rows("publications.csv")
    for r in rows:
        r["authors_html"] = _format_authors(r["authors"], pi_surnames, lab_surnames)
        r["badge_label"] = r["venue_short"]
        # Link buttons — only those filled in the CSV are emitted.
        # project page -> project/publisher page, arxiv -> arXiv, code -> GitHub.
        links = []
        for key, label, icon in (("project page", "Project Page", "globe"),
                                 ("arxiv", "arXiv", "arxiv"),
                                 ("code", "Code", "github")):
            val = r[key]
            if not val:
                continue
            if key == "arxiv" and not val.startswith("http"):
                val = f"https://arxiv.org/abs/{val}"
            links.append({"label": label, "url": val, "icon": icon})
        r["links"] = links
        # The title points at the published version, not whichever button
        # happens to come first, so it never lands on arXiv for a paper that
        # has a publisher record. Blank means the title is not a link.
        r["url"] = r["venue_url"]
    # Newest year first, then the order column within each year — so the
    # sequence is stated in the CSV rather than inherited from row order.
    _int_column(rows, "year", "publications.csv")
    _int_column(rows, "order", "publications.csv")
    rows.sort(key=lambda r: (-r["year"], r["order"]))
    years = sorted({r["year"] for r in rows if r["year"]}, reverse=True)
    by_year = [{"year": y, "items": [r for r in rows if r["year"] == y]} for y in years]
    types = sorted({r["venue_type"] for r in rows if r["venue_type"]})
    span = (f"{years[-1]}–{years[0]}" if len(years) > 1 else (years[0] if years else ""))
    return {"all": rows, "by_year": by_year, "years": years, "types": types,
            "recent": rows[:recent_count],
            "count": len(rows), "year_span": span, "venue_count": len({r["venue_short"] for r in rows if r["venue_short"]})}


def _meta_excerpt(text: str, limit: int) -> str:
    """The opening of `text`, cut at a word boundary, for a meta description."""
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0].rstrip(",;:.\u2014- ") + "\u2026"


def load_research() -> list[dict]:
    rows = _read_rows("research.csv")
    _int_column(rows, "order", "research.csv")
    for r in rows:
        r["num"] = ""  # filled below
    rows.sort(key=lambda r: r["order"])
    for i, r in enumerate(rows, 1):
        r["num"] = f"{i:02d}"
        r["url"] = f"{r['slug']}.html"
    return rows


def load_join_criteria() -> list[dict]:
    rows = _read_rows("join_criteria.csv")
    _int_column(rows, "order", "join_criteria.csv")
    rows.sort(key=lambda r: r["order"])
    return rows


def load_join_steps() -> list[dict]:
    """`html` may carry inline links, so join.html renders it raw."""
    rows = _read_rows("join_steps.csv")
    _int_column(rows, "order", "join_steps.csv")
    rows.sort(key=lambda r: r["order"])
    return rows


def load_news() -> list[dict]:
    rows = _read_rows("news.csv")
    def parse(d):
        for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
            try:
                return datetime.strptime(d, fmt).date()
            except (ValueError, TypeError):
                continue
        return date(1900, 1, 1)
    for r in rows:
        d = parse(r["date"])
        r["_date"] = d
        r["date_display"] = d.strftime("%b %Y") if d.year > 1900 else r["date"]
        r["date_iso"] = d.isoformat() if d.year > 1900 else ""
        tag = r["tag"]
        r["glyph"] = {"publication": "PUB", "lab": "LAB", "award": "AWD",
                      "talk": "TLK", "join": "JOB"}.get(tag.lower(),
                      tag[:3].upper())
    rows.sort(key=lambda r: r["_date"], reverse=True)
    return rows


def load_positions() -> list[dict]:
    return _read_rows("positions.csv")


# --------------------------------------------------------------------------- #
#  Tiny template engine  ({{ var }}, {% for %}, {% if %}, {% include %})       #
# --------------------------------------------------------------------------- #
_TOKEN = re.compile(r"({%.*?%}|{{.*?}}|{#.*?#})", re.S)


class _Node:
    pass


class _Text(_Node):
    def __init__(self, s): self.s = s
    def render(self, ctx, env): return self.s


class _Var(_Node):
    def __init__(self, expr):
        parts = [p.strip() for p in expr.split("|")]
        self.path = parts[0]
        self.filters = parts[1:]
    def render(self, ctx, env):
        val = _lookup(self.path, ctx)
        if val is _MISSING:
            raise SystemExit(f"templates/{env['template']}: {{{{ {self.path} }}}} is not "
                             f"defined — check the spelling, or add the column/key in data/")
        out = "" if val is None else str(val)
        raw = False
        for f in self.filters:
            if f == "raw":
                raw = True
            elif f == "upper":
                out = out.upper()
            elif f == "lower":
                out = out.lower()
            elif f == "title":
                out = out.title()
            elif f == "urlencode":
                from urllib.parse import quote
                out = quote(out)
            elif f == "nl2br":
                out = html.escape(out).replace("\n", "<br>")
                raw = True
        return out if raw else html.escape(out)


class _For(_Node):
    def __init__(self, var, coll, body):
        self.var, self.coll, self.body = var, coll, body
    def render(self, ctx, env):
        items = _lookup(self.coll, ctx)
        if items is _MISSING:
            raise SystemExit(f"templates/{env['template']}: {{% for {self.var} in "
                             f"{self.coll} %}} is not defined — check the spelling, "
                             f"or add the column/key in data/")
        items = items or []
        out = []
        n = len(items)
        for i, item in enumerate(items):
            child = dict(ctx)
            child[self.var] = item
            child["loop"] = {"index": i + 1, "index0": i, "first": i == 0,
                             "last": i == n - 1, "length": n, "even": (i % 2 == 1),
                             "odd": (i % 2 == 0)}
            out.append(_render_nodes(self.body, child, env))
        return "".join(out)


class _If(_Node):
    def __init__(self, branches, els):
        self.branches = branches  # list of (cond_str, body_nodes)
        self.els = els
    def render(self, ctx, env):
        for cond, body in self.branches:
            if _truthy(cond, ctx):
                return _render_nodes(body, ctx, env)
        return _render_nodes(self.els, ctx, env)


class _Include(_Node):
    def __init__(self, name): self.name = name.strip().strip("'\"")
    def render(self, ctx, env):
        tpl = env["loader"](self.name)
        return _render_nodes(tpl, ctx, {**env, "template": self.name})


# A name the data never defines is a typo or a deleted CSV column; an empty
# cell is a legitimately blank optional value. Only the first is an error.
_MISSING = object()


def _lookup(path, ctx):
    if path.startswith(("'", '"')):
        return path.strip("'\"")
    cur = ctx
    for part in path.split("."):
        if isinstance(cur, dict):
            if part not in cur:
                return _MISSING
            cur = cur[part]
        else:
            cur = getattr(cur, part, _MISSING)
        if cur is _MISSING:
            return _MISSING
        if cur is None:
            return None
    return cur


def _truthy(expr, ctx):
    expr = expr.strip()
    if expr.startswith("not "):
        return not _truthy(expr[4:], ctx)
    for op in ("==", "!="):
        if op in expr:
            l, r = expr.split(op, 1)
            lv = _lookup(l.strip(), ctx)
            rv = _lookup(r.strip(), ctx)
            lv = "" if lv is _MISSING else lv
            rv = "" if rv is _MISSING else rv
            return (str(lv) == str(rv)) if op == "==" else (str(lv) != str(rv))
    val = _lookup(expr, ctx)
    if val is _MISSING:
        return False
    if isinstance(val, (list, dict, str)):
        return len(val) > 0
    return bool(val)


def _parse(tokens, idx, stop):
    nodes = []
    while idx < len(tokens):
        tok = tokens[idx]
        if tok == "":
            idx += 1
            continue
        if tok.startswith("{#"):
            idx += 1
            continue
        if tok.startswith("{{"):
            nodes.append(_Var(tok[2:-2].strip()))
            idx += 1
            continue
        if tok.startswith("{%"):
            stmt = tok[2:-2].strip()
            head = stmt.split(" ", 1)[0]
            if head in stop:
                return nodes, idx, head
            if head == "for":
                m = re.match(r"for\s+(\w+)\s+in\s+(.+)", stmt)
                body, idx, _ = _parse(tokens, idx + 1, {"endfor"})
                nodes.append(_For(m.group(1), m.group(2).strip(), body))
                idx += 1
            elif head == "if":
                branches = []
                cond = stmt.split(" ", 1)[1].strip()  # text after "if"
                els = []
                while True:
                    body, idx, end = _parse(tokens, idx + 1, {"elif", "else", "endif"})
                    branches.append((cond, body))
                    if end == "elif":
                        cond = tokens[idx][2:-2].strip().split(" ", 1)[1].strip()
                        continue
                    if end == "else":
                        els, idx, _ = _parse(tokens, idx + 1, {"endif"})
                    break
                nodes.append(_If(branches, els))
                idx += 1
            elif head == "include":
                nodes.append(_Include(stmt[len("include"):].strip()))
                idx += 1
            else:
                idx += 1
            continue
        nodes.append(_Text(tok))
        idx += 1
    return nodes, idx, None


def _render_nodes(nodes, ctx, env):
    return "".join(n.render(ctx, env) for n in nodes)


_PARSE_CACHE: dict[str, list] = {}


def _compile(name: str) -> list:
    if name not in _PARSE_CACHE:
        src = (TPL / name).read_text(encoding="utf-8")
        tokens = _TOKEN.split(src)
        nodes, _, _ = _parse(tokens, 0, set())
        _PARSE_CACHE[name] = nodes
    return _PARSE_CACHE[name]


def render(name: str, ctx: dict) -> str:
    env = {"loader": _compile, "template": name}
    return _render_nodes(_compile(name), ctx, env)


# --------------------------------------------------------------------------- #
#  Build                                                                       #
# --------------------------------------------------------------------------- #
def _build_jsonld(site: dict, pi: dict) -> str:
    import json
    data = {
        "@context": "https://schema.org",
        "@type": "ResearchOrganization",
        "name": site["lab_full_name"],
        "alternateName": site["lab_name"],
        "url": site["site_url"],
        "logo": site["site_url"] + "assets/img/brand/icon-512.png",
        "image": site["site_url"] + "assets/img/brand/og-image.png",
        "description": site["meta_description"],
        "email": site["email"],
        "parentOrganization": {"@type": "CollegeOrUniversity",
                               "name": site["university"]},
        "address": {"@type": "PostalAddress",
                    "streetAddress": site["office"],
                    "addressLocality": site["address_locality"],
                    "addressCountry": site["address_country"]},
    }
    if pi:
        # url is the PI's page on this site; external profiles go in sameAs.
        founder = {"@type": "Person", "name": pi["name"],
                   "jobTitle": pi["role"],
                   "url": site["site_url"] + pi["url"]}
        if pi["orcid"]:
            # ORCID is the canonical identifier for a researcher, so expose it
            # next to the name rather than only on the page.
            founder["identifier"] = "https://orcid.org/" + pi["orcid"]
        same_as = [u for u in ("https://orcid.org/" + pi["orcid"] if pi["orcid"] else "",
                               pi["scholar"], pi["website"]) if u]
        if same_as:
            founder["sameAs"] = same_as
        data["founder"] = founder
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def base_context() -> dict:
    site = load_site()
    pages = load_pages()
    members = load_members()
    # Author highlighting reads its surnames from members.csv, so a rename
    # there can never leave a stale name behind in this file.
    pi_surnames = {_fold(members["pi"]["surname"])} if members["pi"] else set()
    lab_surnames = {_fold(m["surname"]) for m in members["all"]
                    if m["surname"] and m is not members["pi"]}
    publications = load_publications(int(site["home_publications_count"]),
                                     pi_surnames, lab_surnames)
    # A member's papers are matched exactly the way author highlighting is, so a
    # profile can never claim a paper its author list does not support.
    for m in members["all"]:
        key = _fold(m["surname"])
        m["publications"] = [p for p in publications["all"]
                             if key and any(key in _fold(tok)
                                            for tok in p["authors"].split(","))] if key else []
    research = load_research()
    news = load_news()
    positions = load_positions()
    join_criteria = load_join_criteria()
    join_steps = load_join_steps()
    return {
        "pages": pages,
        "join_criteria": join_criteria,
        "join_steps": join_steps,
        "jsonld": _build_jsonld(site, members["pi"]),
        "site": site,
        "members": members,
        "publications": publications,
        "research": research,
        "news": news,
        "news_recent": news[:5],
        "positions": positions,
        "nav": [{"id": p["id"], "label": p["nav_label"], "url": p["output"]} for p in pages],
        "year_now": str(datetime.now().year),
    }


def build(out_dir: Path = OUT) -> list[Path]:
    ctx = base_context()
    written = []
    site_url = ctx["site"]["site_url"]
    for page in ctx["pages"]:
        output = page["output"]
        page_ctx = dict(ctx)
        page_ctx["page"] = page["id"]
        page_ctx["page_title"] = page["title"]
        page_ctx["page_desc"] = page["meta_description"]
        page_ctx["page_url"] = site_url + ("" if output == "index.html" else output)
        page_ctx["site_url"] = site_url
        page_ctx["nav"] = [dict(n, active=(n["id"] == page["id"])) for n in ctx["nav"]]
        html_out = render(page["template"], page_ctx)
        target = out_dir / output
        target.write_text(html_out, encoding="utf-8")
        written.append(target)
    # One page per research area, generated from research.csv rather than listed
    # in pages.csv, so adding an area stays a one-row change.
    taken = {p["output"] for p in ctx["pages"]}
    for area in ctx["research"]:
        output = area["url"]
        if output in taken:
            raise ValueError(f"research slug {area['slug']!r} would overwrite {output}")
        page_ctx = dict(ctx)
        page_ctx["page"] = "research"
        page_ctx["area"] = area
        page_ctx["page_title"] = f"{area['title']} \u2014 {ctx['site']['lab_full_name']}"
        page_ctx["page_desc"] = _meta_excerpt(area["description"], 160)
        page_ctx["page_url"] = site_url + output
        page_ctx["site_url"] = site_url
        page_ctx["nav"] = [dict(n, active=(n["id"] == "research")) for n in ctx["nav"]]
        taken.add(output)
        target = out_dir / output
        target.write_text(render("research-area.html", page_ctx), encoding="utf-8")
        written.append(target)
    # One page per member, generated from members.csv the same way.
    for m in ctx["members"]["all"]:
        output = m["url"]
        if output in taken:
            raise ValueError(f"member slug {m['slug']!r} would overwrite {output}")
        taken.add(output)
        page_ctx = dict(ctx)
        page_ctx["page"] = "team"
        page_ctx["m"] = m
        page_ctx["page_title"] = f"{m['name']} \u2014 {ctx['site']['lab_full_name']}"
        page_ctx["page_desc"] = _meta_excerpt(
            m["bio"] or f"{m['name']}, {m['role']}, {ctx['site']['lab_full_name']}.", 160)
        page_ctx["page_url"] = site_url + output
        page_ctx["site_url"] = site_url
        page_ctx["nav"] = [dict(n, active=(n["id"] == "team")) for n in ctx["nav"]]
        target = out_dir / output
        target.write_text(render("member.html", page_ctx), encoding="utf-8")
        written.append(target)
    # sitemap + robots
    _write_sitemap(ctx, out_dir)
    return written


def _write_sitemap(ctx, out_dir):
    base = ctx["site"]["site_url"]
    paths = ["" if p["output"] == "index.html" else p["output"] for p in ctx["pages"]]
    paths += [a["url"] for a in ctx["research"]]
    paths += [m["url"] for m in ctx["members"]["all"]]
    urls = "".join(f"  <url><loc>{base}{p}</loc></url>\n" for p in paths)
    (out_dir / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}</urlset>\n", encoding="utf-8")
    (out_dir / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {base}sitemap.xml\n", encoding="utf-8")


def main(argv):
    if "--check" in argv:
        import tempfile
        tmp = Path(tempfile.mkdtemp(prefix="neuravision-check-"))
        written = build(tmp)
        print(f"✓ check OK — {len(written)} pages built into {tmp} (repo not modified)")
        shutil.rmtree(tmp, ignore_errors=True)
        return
    written = build()
    print(f"✓ built {len(written)} pages:")
    for p in written:
        print(f"    {p.relative_to(ROOT)}")
    if "--serve" in argv:
        import http.server, socketserver, os
        os.chdir(ROOT)
        port = 8000
        print(f"\n→ serving http://localhost:{port}  (Ctrl-C to stop)")
        with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as httpd:
            httpd.serve_forever()


if __name__ == "__main__":
    main(sys.argv[1:])
