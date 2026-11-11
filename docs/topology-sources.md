# Topology page: sources and figures

Checked 2026-11-12 against [Doruk Öner’s Google Scholar profile](https://scholar.google.com/citations?user=ESA2CsAAAAAJ&hl=en), original papers and publisher records. Scholar was accessible through the browser. The initial bibliography includes eight relevant method/application papers; the 2023 thesis is a separate further-reading link. This is a curated topic selection, not an assertion that every paper on the profile concerns topology.

Following the user's request, bibliography membership now comes automatically from the `topology` tag in `data/publications.csv`, matched against the topic's `publication_tag` in `data/research.csv`. The initial eight papers were migrated to that tag. Future tagged publications appear on rebuild without an article edit or separate mapping. The narrative and figure captions remain curated text and are not automatically generated for newly tagged papers.

The article distinguishes current NeuraVision work (CAPE) from earlier EPFL and collaborative work. Text is an original explanatory synthesis, not copied abstracts. No new benchmark claims or performance numbers have been introduced.

## Scientific sources and scope

| Work | Primary sources | Used for |
|---|---|---|
| CAPE, MICCAI 2025 | [arXiv 2504.00753](https://arxiv.org/abs/2504.00753), [lab project](https://neuravisionlab.com/CAPE/), [proceedings](https://link.springer.com/chapter/10.1007/978-3-032-05162-2_18) | Skeleton node-pair sampling; predicted shortest paths; path masking to prevent loop detours; regression plus path loss; 2D CREMI/DRIVE and 3D mouse brain. Read the current arXiv v2 and project material. |
| Region separation, TPAMI 2022 | [arXiv 2009.07011](https://arxiv.org/abs/2009.07011), [publisher DOI](https://doi.org/10.1109/TPAMI.2021.3074366) | Background-region separation as connectivity supervision; distance maps and annotation dilation; roads/canals; why this does not directly extend to 3D curves. The journal volume year is 2022; online-first DOI date is 2021. |
| PH with improved locality, TPAMI 2023 | [arXiv 2110.06295](https://arxiv.org/abs/2110.06295), [publisher DOI](https://doi.org/10.1109/TPAMI.2023.3246921) | Threshold/height-function filtration gives persistence diagrams additional spatial information; roads and neurites; do not claim full recovery of spatial positions or guaranteed topology. |
| Adjusting annotations, TMI 2022 | [arXiv 2112.02781](https://arxiv.org/abs/2112.02781), [publisher DOI](https://doi.org/10.1109/TMI.2022.3193072) | Active-contour graphs and joint annotation/network optimization; microscopy; reliable topology but imperfect geometry is the premise. Not a method for recovering arbitrary missing branches. |
| Connectivity through projections, MICCAI 2022 | [arXiv 2207.06832](https://arxiv.org/abs/2207.06832), [proceedings](https://link.springer.com/chapter/10.1007/978-3-031-16443-9_57) | Three orthogonal minimum-intensity projections of distance maps; 2D loss and annotations; microscopy/MRA; projection overlap can conceal gaps. |
| TOPO-Loss for cracks, CBM 2022 | [publisher article](https://doi.org/10.1016/j.conbuildmat.2022.128264) | Continuity-preserving crack detection in earthquake-damaged masonry and coarse annotations. Read the publisher HTML; no figure extracted. |
| Power-line cables and pylons, MVA 2025 | [arXiv 2407.14352](https://arxiv.org/abs/2407.14352), [publisher article](https://doi.org/10.1007/s00138-025-01664-1) | Aircraft imagery, distance-map heads for cables/pylons and cable-connectivity term. No claim of certified safety or deployed collision avoidance. |
| Drainage canals, AGU Advances 2021 | [publisher DOI](https://doi.org/10.1029/2020AV000321), [public full text](https://par.nsf.gov/servlets/purl/10251534), [MIT repository](https://dspace.mit.edu/entities/publication/81089308-9539-4d2b-91be-5bc8805a1491) | Satellite-image canal mapping in Southeast Asian peatlands and its role in drainage, subsidence and carbon analysis. No causal claims beyond the article. |
| Doctoral thesis, EPFL 2023 | [thesis DOI](https://doi.org/10.5075/epfl-thesis-9749) | Further reading on the earlier work, not an additional current-lab paper. |

## Figure provenance

The five paper figures below are faithful extracts or author-hosted assets. Only bounding whitespace/captions outside the figure were cropped; no scientific panels, annotations or colors were retouched. Original panel labels remain. Captions on the website identify the paper and figure and link to the source. Every figure also opens as an image at its saved resolution. Scientific figures retain a white backing in both themes.

All crop coordinates below are PDF points `(left, top, right, bottom)`, with pages numbered from 1. PDFs were rendered through pdfplumber/PDFium at 300 dpi and encoded as high-quality WebP. This is faithful rasterization, not AI image generation. Source PDFs remain outside the website in the local task scratch directory.

| Local file under `assets/img/research/topology/` | Origin | Extraction | Saved dimensions |
|---|---|---|---|
| `cape-path-masking.webp` | CAPE Fig. 2, [author-hosted image](https://neuravisionlab.com/CAPE/static/images/FIG_MASK.png) | Whole image; downsampled from 5263 × 3255; quality 93 | 1800 × 1113 |
| `region-comparison.webp` | Region separation, Fig. 1, arXiv PDF page 2 | `(46, 41, 303, 260)`; quality 94 | 1070 × 912 |
| `locality-comparison.webp` | Improved locality, Fig. 1, arXiv PDF page 2 | `(132, 40, 470, 220)`; quality 94 | 1408 × 750 |
| `annotation-adjustment.webp` | Annotation adjustment, Fig. 2, arXiv PDF page 1 | `(310, 456, 562, 533)`; quality 94 | 1050 × 320 |
| `projection-diagram.webp` | Connectivity through projections, Fig. 2, arXiv PDF page 4 | `(375, 417, 483, 510)`; quality 94 | 450 × 387 |

The opening conceptual illustration is the existing `assets/img/home/topology.webp`, the same informative image used on the research overview. It is explicitly described as conceptual in its alt text and is not presented as a measured result from a paper. No figures from the presentation or homepage were regenerated.

## Corrected publication links

The CSV had unrelated arXiv IDs for five included papers; they were replaced with the verified IDs above. The crack paper's unrelated arXiv link was removed because no corresponding preprint was verified. The canal paper had a publisher URL in its arXiv field; this was removed and its open MIT repository record was added as the project-page link. Code links for locality, annotation adjustment and projections were verified from their original papers. These corrections also propagate to the general bibliography and author pages through the shared publication data.

This page remains a local draft. Publishing is outside this task's scope.
