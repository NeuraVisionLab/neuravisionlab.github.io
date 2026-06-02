# NeuraVision Research Lab — website

The website for the **NeuraVision Research Lab** (Computer Vision & Deep Learning,
Department of Computer Engineering, Bilkent University — PI Dr. Doruk Öner).

A clean, fast, **static** site generated from CSV files by a tiny zero-dependency
Python build script. All content lives in `data/*.csv`, so updating the site never
requires touching HTML or CSS. The template layer is a small Jinja-like subset, so
moving to a dynamic backend later (Flask/Jinja2, Eleventy, Next.js, a CMS…) is
straightforward.

```
Edit data/*.csv   →   python3 build.py   →   static *.html   →   GitHub Pages
```

## Quick start

```bash
# build the site (no dependencies beyond Python 3.8+)
python3 build.py

# build and preview locally at http://localhost:8000
python3 build.py --serve
```

Then open `index.html` (or the local server URL).

## Editing content

Everything is data-driven. Edit a CSV in `data/`, run `python3 build.py`, and the
pages regenerate. No CSV requires HTML knowledge.

| File | What it controls |
|------|------------------|
| `data/site.csv` | Lab name, tagline, hero copy, contact details, map, social links, headline stats. Simple `key,value` rows. |
| `data/members.csv` | The team. One row per person. `group=pi` is the principal investigator; everyone else is a researcher. Photos live in `assets/img/people/` and are referenced by the `photo` column. Leave `bio`/`scholar`/`github`/`website` blank if unknown — the templates handle empty fields. |
| `data/publications.csv` | Publication list. Set `featured=yes` to surface a paper on the home page. Fill `pdf` / `code` / `project` / `arxiv` / `doi` to add link buttons (bare arXiv IDs and DOIs are turned into full URLs automatically). |
| `data/research.csv` | Research areas shown on the home page and the Research page (zig-zag blocks). |
| `data/news.csv` | The "Lab news" log. Newest first; the most recent entry is flagged **NEW**. |
| `data/positions.csv` | Open positions on the Join page. |

**Adding a team member:** drop a portrait in `assets/img/people/` (a 3:4 portrait
JPEG looks best), add a row to `members.csv` with `photo` pointing at it, rebuild.
Photos are shown in greyscale and bloom to colour on hover.

**Lab-author highlighting** in publication lists is automatic: surnames listed in
`build.py` (`_PI_SURNAMES` / `_LAB_SURNAMES`) are bolded, with the PI in green. Add a
new student's surname there if you want their name emphasised in author lists.

## Deploying to GitHub Pages

A workflow at `.github/workflows/deploy.yml` rebuilds and deploys on every push to
`main`/`master`:

1. Create a GitHub repo and push this folder.
2. In **Settings → Pages**, set **Source = GitHub Actions**.
3. Push. The Action runs `python3 build.py` and publishes the result.

Pre-built HTML is also committed, so the site works even without the Action (e.g. if
you set Pages to "Deploy from a branch").

Using a **custom domain** or a different repo name? Update `SITE_URL` near the top of
`build.py` (used for canonical URLs, the sitemap and social-share tags), put your
domain in a `CNAME` file, and rebuild. All asset/page links are relative, so the site
works both at a domain root and under `username.github.io/repo/`.

## Project structure

```
.
├── data/            # ← single source of truth (CSV)
├── templates/       # HTML templates (Jinja-like: {{ var }}, {% for %}, {% if %}, {% include %})
├── assets/
│   ├── css/styles.css
│   ├── js/main.js   # nav, mobile drawer, scroll reveal, count-up, publication filter
│   ├── fonts/       # self-hosted Jura, Inter, IBM Plex Mono (woff2)
│   └── img/
│       ├── brand/   # logo, marks, favicons, og-image
│       └── people/  # member portraits
├── build.py         # the generator (stdlib only)
├── index.html …     # generated pages (do not edit by hand — edit CSV + templates)
└── .github/workflows/deploy.yml
```

## Design

A light, editorial "paper" reading surface with two dark anchors (the home hero and
the footer) and compact dark sub-heroes on inner pages. Brand green `#28B560` is used
sparingly as accent "data-ink" (links, rules, the node-constellation motif, the
primary button). Typography pairs **Jura** (display/wordmark/labels) with **Inter**
(body) and **IBM Plex Mono** (indices, venue tags, coordinates). Fully responsive,
keyboard-accessible, and respects `prefers-reduced-motion`.

## Extending to a dynamic site

The data model (`load_*` functions in `build.py`) and the Jinja-like templates port
almost directly to Jinja2/Flask or Eleventy. Swap the CSV loaders for database/API
calls, keep the templates, and the same markup renders server-side or client-side.

---

Built static · served on GitHub Pages.
