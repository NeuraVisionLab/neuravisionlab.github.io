# NeuraVision Research Lab — website

The website for the **NeuraVision Research Lab** (Computer Vision & Deep Learning,
Department of Computer Engineering, Bilkent University — PI Dr. Doruk Öner).

**Live at: https://neuravisionlab.github.io/**

A clean, modern, **static** site generated from CSV files by a tiny zero-dependency
Python script. **Every piece of content lives in `data/*.csv`** — you never have to
touch HTML or CSS to update the site. It has a light/dark theme toggle, an animated
node-graph that follows your mouse, and publication link buttons that appear only
when you provide a link.

```
Edit data/*.csv   →   python3 build.py   →   static *.html   →   GitHub Pages
```

## Quick start

```bash
python3 build.py            # build the site (needs only Python 3.8+)
python3 build.py --serve    # build, then preview at http://localhost:8000
python3 build.py --check    # build into a temp dir to verify, without writing
```

Open `index.html` (or the preview URL). After editing any CSV, run `python3 build.py`
again (or just push — the GitHub Action rebuilds for you, see *Deploying*).

---

## Editing content — everything is a CSV

All files live in **`data/`**. Commas inside a field are fine if you wrap the field
in `"double quotes"` (any spreadsheet — Excel, Numbers, Google Sheets — does this for
you when you export as CSV).

### `site.csv` — global text & settings (`key,value`)
Lab name, tagline, **hero headline**, contact details, map, social links, default
theme. Notable keys:

| key | what it does |
|-----|--------------|
| `hero_headline` | The big headline on the home page. |
| `hero_accent` | One word from the headline to highlight in green (e.g. `topology`). |
| `hero_subhead` | The sentence under the headline. |
| `tagline`, `meta_description`, `intro_heading`, `intro_body` | Home/about + SEO text. |
| `email`, `phone`, `office`, `address`, `department`, `university`, `city` | Contact block + footer. |
| `map_query`, `map_lat`, `map_lng` | Contact map (an OpenStreetMap embed + "directions" link are generated from these). |
| `scholar_url`, `github_url`, `linkedin_url`, `x_url` | Footer / profile links (leave blank to hide). |
| `default_theme` | `auto` (follow the visitor's system), `light`, or `dark`. |

> Stats shown on the site (e.g. the Publications page's Papers · Venues · Years)
> are **counted automatically** from the CSVs, so they're always correct — and
> there are no citation counts anywhere on the site.

### `members.csv` — the team
One row per person. `group=pi` is the principal investigator; everyone else is a
researcher (shown in the grid, indexed M1, M2 …). `order` controls the sort.

- `photo` points at a file in `assets/img/people/` (a 3:4 portrait JPEG looks best).
- `interests` is a `;`-separated list; the first one shows as the card's tag.
- Leave `bio` / `scholar` / `github` / `website` blank if unknown — empty fields are
  simply not rendered. If `photo` is blank, an initials tile is shown instead.

**Add a member:** drop a portrait in `assets/img/people/`, add a row pointing `photo`
at it, rebuild.

### `publications.csv` — papers & link buttons
Columns: `id, year, title, authors, venue, venue_type, venue_short, featured,
paper, arxiv, code`.

The three link columns become buttons **only when filled** — leave one blank and that
button simply doesn't appear:

| column | button | put here |
|--------|--------|----------|
| `paper` | **Paper** | the conference/journal page (proceedings, DOI, publisher). |
| `arxiv` | **arXiv** | the arXiv abstract URL — or just the bare id like `1803.04039`. |
| `code` | **Code** | the GitHub (or other) repository URL. |

Other fields: set `featured=yes` to surface a paper on the home page; `venue_type`
(`journal`/`conference`/`preprint`/`dataset`/`thesis`) is a column you set — the filter
pills are generated from whichever values appear; `venue_short` (e.g. `TPAMI`, `MICCAI`) is the badge label, and
the top venues get a green dot. Lab members are **bold** in the author list and the PI
is shown in green automatically (surnames are configured in `build.py`).

### `research.csv` — research areas
`order, slug, title, tag, summary, description`. Shown as cards on the home page and
as the zig-zag blocks on the Research page. Add/remove rows freely.

### `news.csv` — the "Lab news" log
`date, title, body, tag, link`. Newest first; the most recent entry is flagged **NEW**.
`tag` (e.g. `Publication`, `Lab`, `Award`, `Talk`) shows as a small glyph. `link` can be
another page (`publications.html`) or any URL; blank = no link.

### `positions.csv` — open positions (Join page)
`title, audience, status, description`.

---

## Theme (light / dark)

There's a toggle (sun/moon) in the header. The choice is remembered in the browser.
The site's **default** is set by `default_theme` in `site.csv` (`auto` follows the
visitor's OS setting). Both themes are fully styled and contrast-checked.

## Fonts

The wordmark/headings use **Jura**, served directly from the brand file you provided
(`NeuravisionBRAND/FONT/Jura-VariableFont_wght.ttf`, compressed to
`assets/fonts/jura-brand.woff2`). Body text uses Inter and labels use IBM Plex Mono,
all self-hosted (no external font requests).

## Deploying to GitHub Pages

This site is published as the **organization site** of `NeuraVisionLab` — the repo is
named **`neuravisionlab.github.io`**, so GitHub serves it at the domain **root**:

> **https://neuravisionlab.github.io/**

### Updating the live site
The built HTML is committed, so any push to `main` updates the site:
```bash
# edit data/*.csv (or templates/assets), then:
python3 build.py
git add -A
git commit -m "Update content"
git push
```
Pages redeploys automatically (usually within a minute).

### How it's wired
- Pre-built HTML is committed, so Pages can simply **Deploy from a branch** (`main` / root)
  — `.nojekyll` makes it serve the files as-is.
- A `.github/workflows/deploy.yml` is also included: if you set **Settings → Pages →
  Source = GitHub Actions**, it runs `python3 build.py` on each push and deploys the
  result (handy so you don't have to commit the generated HTML yourself).

### Custom domain / different repo
Edit `SITE_URL` near the top of `build.py` (used for canonical URLs, the sitemap and
share cards), rebuild, and — for a custom domain — add a `CNAME` file. All links are
relative, so the site also works under a project path like `username.github.io/repo/`.

## Project structure

```
.
├── data/            # ← single source of truth (CSV)
├── templates/       # HTML templates (Jinja-like: {{ var }}, {% for %}, {% if %}, {% include %})
├── assets/
│   ├── css/styles.css
│   ├── js/main.js   # theme toggle, mouse parallax, nav, mobile drawer, reveal, filter
│   ├── fonts/       # self-hosted Jura (your brand file), Inter, IBM Plex Mono
│   └── img/{brand,people}/
├── build.py         # the generator (Python standard library only)
├── index.html …     # generated pages (don't edit by hand — edit CSV + templates)
└── .github/workflows/deploy.yml
```

## Extending to a dynamic site

The data loaders in `build.py` and the Jinja-like templates port almost directly to
Jinja2/Flask or Eleventy: swap the CSV loaders for database/API calls, keep the
templates. The same markup then renders server-side or client-side.

---

Built static · served on GitHub Pages.
