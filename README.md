# NeuraVision Research Lab — website

**Live at <https://neuravisionlab.com>**

Everything on the site comes from the CSV files in **`data/`**.
Edit a CSV, commit — the site rebuilds and republishes itself in a minute or two.
You never need to touch HTML, CSS, or run anything.

> The `.html` files in the root are **generated**. Don't edit them; edit the CSV.

---

## What do I edit?

| I want to… | Edit |
|---|---|
| Add a paper | `data/publications.csv` |
| Add or update a person | `data/members.csv` |
| Post lab news | `data/news.csv` |
| Change or add a research area (each gets its own page) | `data/research.csv` |
| Open or close a position | `data/positions.csv` |
| Change any heading, button or paragraph | `data/site.csv` |
| Change page titles, nav or SEO text | `data/pages.csv` |

**How:** open the file on GitHub → pencil icon → edit → *Commit changes*. That's it.

A field you leave blank is simply not shown — a member with no GitHub link
just doesn't get one. Commas inside a value are fine if you wrap it in
`"double quotes"`; every spreadsheet does this automatically.

---

## Adding a paper

Add one row to `data/publications.csv`:

| Column | What to put |
|---|---|
| `order` | Position **within its year**, lower first. Also decides what appears on the home page. |
| `year` | Groups the list. Use the year it was *published*, not the preprint year. |
| `title`, `authors` | As printed. Lab members are bolded automatically. |
| `venue`, `venue_short` | Full venue, and the short badge label (`MICCAI`, `TPAMI`). |
| `venue_type` | `journal`, `conference`, `preprint`, `dataset` or `thesis` — this makes the filter pills. |
| `venue_url` | **Where it's published** (proceedings / journal / DOI page). The title links here. |
| `project page`, `arxiv`, `code` | The three icon buttons. Each appears only if you fill it. |
| `bibtex` | What the **Cite** button copies. |

For `bibtex`, paste the publisher's own BibTeX (the "Cite" or "Export citation"
link on the paper's page). Keep the whole entry in the one cell — multi-line is
fine. Wrap acronyms in the title in an extra `{ }` so they survive, e.g.
`title = {{CAPE: Connectivity-Aware …}}`, otherwise some styles print "Cape".

---

## Adding a person

Drop a portrait in `assets/img/people/` (portrait crop — cards show 4:5, the PI
 photo 3:4 — name it `first-last.jpg`),
then add a row to `data/members.csv`:

- `photo` — the filename you just added. Blank shows initials instead.
- `surname` — how papers credit them. This is what bolds their name in the
  publication list, so it must match the author string (`Fallah`, not `Ardalani`).
- `interests` — `;`-separated; the first one becomes the card's tag.
- `orcid` — bare iD (`0000-0002-…`). Currently shown for the PI.
- `group` — `pi` for the principal investigator, anything else for researchers.
- `order` — position in the grid.

---

## The other files

- **`research.csv`** — one row per area, and **each row becomes its own page**
  at `<slug>.html`, linked from the home page, the research page and the footer.
  `description` is the text shown everywhere — home card, research page and the
  area's own page. `image` names a file in `assets/img/research/` (square; the
  card crops it); blank falls back to the node graphic. Add a row and you get a
  new page with no other change.
- **`news.csv`** — `date, title, body, tag, link`. Sorted newest first
  automatically; the newest gets a **New** badge. `tag` is e.g. `Publication` or `Lab`.
- **`positions.csv`** and **`join_criteria.csv` / `join_steps.csv`** — the Join page.
- **`site.csv`** — `key,value`. Every heading, eyebrow, lead paragraph and button
  label, keyed by page (`home_*`, `team_*`, `contact_*`, `join_*`, `footer_*`).
  `map_embed` holds the contact-page map: paste the `src` from any map embed.
  `map_lat` / `map_lng` drive the coordinate readout and the directions link, so
  keep them pointing at the same place as the embed.
- **`pages.csv`** — one row per page: its nav label and order, `<title>` and
  meta description.

---

## Running it locally (optional)

Only needed if you want to preview before pushing. Python 3.8+, nothing to install.

```bash
python3 build.py            # rebuild the pages
python3 build.py --serve    # preview at http://localhost:8000
```

If you work locally, run `python3 build.py` before committing so the generated
pages match your CSV edits.

```
data/         ← the only thing you normally edit
templates/    page templates
assets/       css, js, fonts, images
build.py      the generator (Python standard library only)
```

Light/dark theme follows the visitor's system by default; change `default_theme`
in `site.csv` to `light` or `dark` to force one.
