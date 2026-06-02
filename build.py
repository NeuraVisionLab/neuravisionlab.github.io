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

PAGES = [
    # (template, output, page-id, title, description-key-or-text)
    ("index.html", "index.html", "home",
     "NeuraVision Research Lab — Computer Vision & Deep Learning, Bilkent University", None),
    ("team.html", "team.html", "team",
     "Team — NeuraVision Research Lab",
     "Meet the NeuraVision Research Lab: principal investigator Dr. Doruk Öner and the graduate researchers working on computer vision and deep learning at Bilkent University."),
    ("research.html", "research.html", "research",
     "Research — NeuraVision Research Lab",
     "Research at NeuraVision: topological deep learning, curvilinear structure delineation, uncertainty estimation, trustworthy AI, medical image analysis and sequential decision making."),
    ("publications.html", "publications.html", "publications",
     "Publications — NeuraVision Research Lab",
     "Publications from the NeuraVision Research Lab, including work at TPAMI, ICML, MICCAI, TMLR and AISTATS."),
    ("join.html", "join.html", "join",
     "Join — NeuraVision Research Lab",
     "Join the NeuraVision Research Lab at Bilkent University. Open positions for MSc and PhD applicants, undergraduate researchers, interns and visitors."),
    ("contact.html", "contact.html", "contact",
     "Contact — NeuraVision Research Lab",
     "Contact the NeuraVision Research Lab, Department of Computer Engineering, EA Building Room 521, Bilkent University, Ankara, Türkiye."),
]
SITE_URL = "https://neuravisionlab.github.io/neuravision/"  # edit for a custom domain

NAV = [
    ("home", "Home", "index.html"),
    ("research", "Research", "research.html"),
    ("publications", "Publications", "publications.html"),
    ("team", "Team", "team.html"),
    ("join", "Join", "join.html"),
    ("contact", "Contact", "contact.html"),
]

# --------------------------------------------------------------------------- #
#  Data loading                                                               #
# --------------------------------------------------------------------------- #
def _read_rows(name: str) -> list[dict]:
    path = DATA / name
    with path.open(encoding="utf-8-sig", newline="") as f:
        return [ {k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f) ]


def load_site() -> dict:
    kv = {}
    with (DATA / "site.csv").open(encoding="utf-8-sig", newline="") as f:
        for row in csv.reader(f):
            if len(row) >= 2 and row[0] != "key":
                kv[row[0].strip()] = row[1].strip()
    # derive an OpenStreetMap (no-cookie) embed url + directions link from coords
    try:
        lat, lng = float(kv.get("map_lat", "")), float(kv.get("map_lng", ""))
        bbox = f"{lng-0.010:.4f},{lat-0.006:.4f},{lng+0.010:.4f},{lat+0.006:.4f}"
        kv["map_embed"] = ("https://www.openstreetmap.org/export/embed.html?"
                           f"bbox={bbox}&layer=mapnik&marker={lat:.5f},{lng:.5f}")
        kv["map_link"] = f"https://www.openstreetmap.org/?mlat={lat:.5f}&mlon={lng:.5f}#map=16/{lat:.5f}/{lng:.5f}"
    except (ValueError, TypeError):
        kv["map_embed"] = ""
        kv["map_link"] = ""
    return kv


def _split_list(value: str) -> list[str]:
    return [p.strip() for p in re.split(r"[;|]", value) if p.strip()]


def load_members() -> dict:
    rows = _read_rows("members.csv")
    for r in rows:
        try:
            r["order"] = int(r.get("order") or 0)
        except ValueError:
            r["order"] = 0
        r["interests_list"] = _split_list(r.get("interests", ""))
        r["tag"] = r["interests_list"][0] if r["interests_list"] else ""
        r["interests_str"] = " · ".join(r["interests_list"])
        r["has_photo"] = bool(r.get("photo"))
        r["initials"] = "".join(w[0] for w in r["name"].split()[:2]).upper()
    rows.sort(key=lambda r: r["order"])
    pi = [r for r in rows if r.get("group") == "pi"]
    students = [r for r in rows if r.get("group") != "pi"]
    pi0 = pi[0] if pi else None
    return {"all": rows, "pi": pi0, "pi_list": ([pi0] if pi0 else []),
            "students": students, "student_count": len(students)}


def _fold(s: str) -> str:
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFKD", s)
                   if not unicodedata.combining(c)).lower()


# surnames of lab members for author highlighting in publication lists
_PI_SURNAMES = {"oner"}
_LAB_SURNAMES = {"esmaeilzadeh", "garaaghaji", "azad", "akar", "fallah",
                 "maleki", "mohammadnezhad", "ozaydin", "sarhangzadeh"}


def _format_authors(authors: str) -> str:
    out = []
    for tok in [t.strip() for t in authors.split(",")]:
        if not tok:
            continue
        folded = _fold(tok)
        cls = None
        if any(s in folded for s in _PI_SURNAMES):
            cls = "pi"
        elif any(s in folded for s in _LAB_SURNAMES):
            cls = "lab"
        esc = html.escape(tok)
        out.append(f'<span class="{cls}">{esc}</span>' if cls else esc)
    return ", ".join(out)


def load_publications() -> dict:
    rows = _read_rows("publications.csv")
    for r in rows:
        r["is_featured"] = (r.get("featured", "").lower() in ("yes", "true", "1"))
        r["authors_html"] = _format_authors(r.get("authors", ""))
        r["is_top"] = r.get("venue_short", "") in {"TPAMI", "ICML", "MICCAI", "TMLR", "AISTATS", "IEEE TMI"}
        r["badge_label"] = r.get("venue_short") or r.get("venue_type", "").title()
        # Link buttons — only those filled in the CSV are emitted.
        # paper -> conference/journal page, arxiv -> arXiv, code -> GitHub.
        links = []
        for key, label in (("paper", "Paper"), ("arxiv", "arXiv"), ("code", "Code")):
            val = r.get(key)
            if not val:
                continue
            if key == "arxiv" and not val.startswith("http"):
                val = f"https://arxiv.org/abs/{val}"
            links.append({"label": label, "url": val})
        r["links"] = links
        # title links to the first available link (paper > arxiv > code)
        r["url"] = next((l["url"] for l in links), "")
    rows.sort(key=lambda r: -(int(r["year"]) if r["year"].isdigit() else 0))
    years = sorted({r["year"] for r in rows if r["year"]}, reverse=True)
    by_year = [{"year": y, "items": [r for r in rows if r["year"] == y]} for y in years]
    featured = [r for r in rows if r["is_featured"]]
    types = sorted({r["venue_type"] for r in rows if r.get("venue_type")})
    span = (f"{years[-1]}–{years[0]}" if len(years) > 1 else (years[0] if years else ""))
    return {"all": rows, "by_year": by_year, "years": years, "types": types,
            "featured": featured, "featured_one": (featured[0] if featured else (rows[0] if rows else None)),
            "count": len(rows), "year_span": span, "venue_count": len({r["venue_short"] for r in rows if r.get("venue_short")})}


def load_research() -> list[dict]:
    rows = _read_rows("research.csv")
    for r in rows:
        try:
            r["order"] = int(r.get("order") or 0)
        except ValueError:
            r["order"] = 0
        r["num"] = ""  # filled below
    rows.sort(key=lambda r: r["order"])
    for i, r in enumerate(rows, 1):
        r["num"] = f"{i:02d}"
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
        d = parse(r.get("date", ""))
        r["_date"] = d
        r["date_display"] = d.strftime("%b %Y") if d.year > 1900 else r.get("date", "")
        r["date_iso"] = d.isoformat() if d.year > 1900 else ""
        tag = r.get("tag", "")
        r["glyph"] = {"publication": "PUB", "lab": "LAB", "award": "AWD",
                      "talk": "TLK", "join": "JOB"}.get(tag.lower(),
                      (tag[:3] or "•").upper())
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
        items = _lookup(self.coll, ctx) or []
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
        return _render_nodes(tpl, ctx, env)


def _lookup(path, ctx):
    if path.startswith(("'", '"')):
        return path.strip("'\"")
    cur = ctx
    for part in path.split("."):
        if isinstance(cur, dict):
            cur = cur.get(part)
        else:
            cur = getattr(cur, part, None)
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
            return (str(lv) == str(rv)) if op == "==" else (str(lv) != str(rv))
    val = _lookup(expr, ctx)
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
    env = {"loader": _compile}
    return _render_nodes(_compile(name), ctx, env)


# --------------------------------------------------------------------------- #
#  Build                                                                       #
# --------------------------------------------------------------------------- #
def _build_jsonld(site: dict, pi: dict) -> str:
    import json
    data = {
        "@context": "https://schema.org",
        "@type": "ResearchOrganization",
        "name": site.get("lab_full_name", "NeuraVision Research Lab"),
        "alternateName": site.get("lab_name", "NeuraVision"),
        "url": SITE_URL,
        "logo": SITE_URL + "assets/img/brand/icon-512.png",
        "image": SITE_URL + "assets/img/brand/og-image.png",
        "description": site.get("meta_description", ""),
        "email": site.get("email", ""),
        "parentOrganization": {"@type": "CollegeOrUniversity",
                               "name": site.get("university", "Bilkent University")},
        "address": {"@type": "PostalAddress",
                    "streetAddress": site.get("office", ""),
                    "addressLocality": "Ankara", "addressCountry": "TR"},
    }
    if pi:
        data["founder"] = {"@type": "Person", "name": pi.get("name", ""),
                           "jobTitle": "Assistant Professor",
                           "url": pi.get("scholar") or SITE_URL + "team.html"}
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def _accent_headline(headline: str, accent: str) -> str:
    """HTML for the hero headline with one word wrapped in .accent (both from CSV)."""
    esc = html.escape(headline)
    if accent:
        a = html.escape(accent)
        esc = esc.replace(a, f'<span class="accent">{a}</span>', 1)
    return esc


def base_context() -> dict:
    site = load_site()
    members = load_members()
    publications = load_publications()
    research = load_research()
    news = load_news()
    positions = load_positions()
    # Headline stats are derived from the data so they are always correct
    # (and citation-free). Edit the underlying CSVs to change them.
    site["stat_publications"] = str(publications["count"])
    site["stat_members"] = str(len(members["all"]))
    site["stat_researchers"] = str(members["student_count"] + (1 if members["pi"] else 0))
    site["stat_areas"] = str(len(research))
    site.setdefault("default_theme", "auto")
    # Hero headline with one accent word highlighted (both from site.csv)
    site["hero_headline_html"] = _accent_headline(site.get("hero_headline", ""),
                                                  site.get("hero_accent", ""))
    return {
        "jsonld": _build_jsonld(site, members.get("pi")),
        "site": site,
        "members": members,
        "publications": publications,
        "research": research,
        "news": news,
        "news_recent": news[:5],
        "positions": positions,
        "nav": [{"id": i, "label": l, "url": u} for i, l, u in NAV],
        "year_now": str(datetime.now().year),
    }


def build(out_dir: Path = OUT) -> list[Path]:
    ctx = base_context()
    written = []
    for template, output, page_id, title, desc in PAGES:
        page_ctx = dict(ctx)
        page_ctx["page"] = page_id
        page_ctx["page_title"] = title
        page_ctx["page_desc"] = desc or ctx["site"].get("meta_description", "")
        page_ctx["page_url"] = SITE_URL + ("" if output == "index.html" else output)
        page_ctx["site_url"] = SITE_URL
        page_ctx["nav"] = [dict(n, active=(n["id"] == page_id)) for n in ctx["nav"]]
        html_out = render(template, page_ctx)
        target = out_dir / output
        target.write_text(html_out, encoding="utf-8")
        written.append(target)
    # sitemap + robots
    _write_sitemap(ctx, out_dir)
    return written


def _write_sitemap(ctx, out_dir):
    base = SITE_URL
    urls = "".join(
        f"  <url><loc>{base}{'' if out == 'index.html' else out}</loc></url>\n"
        for _, out, *_ in PAGES
    )
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
