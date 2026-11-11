# Uncertainty and 3D research articles: sources

Prepared 2026-11-12 from public primary sources. The author-approved topology
layout is reused. The overview illustrations are the existing informative
research images; scientific figures retain their source colors and labels.
All captions link to the original paper and the full-size local figure.

## Uncertainty

- **Stochastic Nonlinearities Improve Uncertainty Estimation** (BMVC 2026):
  [lab project](https://neuravisionlab.com/Stochastic-Activations-BMVC/) and
  [arXiv 2610.29875v1](https://arxiv.org/abs/2610.29875v1).
  `stochastic-passes.webp` is a lossless WebP conversion of the author's
  [method-overview.png](https://neuravisionlab.com/Stochastic-Activations-BMVC/assets/method-overview.png),
  corresponding to paper Fig. 1. Copy explains switching nonlinearities during
  training/inference, repeated prediction variance, and experiments across
  classification, segmentation and OOD detection. Multiple inference passes are
  still required; no claim of cost-free uncertainty or guaranteed calibration.
- **Enabling Uncertainty Estimation in Iterative Neural Networks** (ICML 2024):
  [proceedings](https://proceedings.mlr.press/v235/durasov24a.html),
  [PDF](https://proceedings.mlr.press/v235/durasov24a/durasov24a.pdf),
  [arXiv 2403.16732](https://arxiv.org/abs/2403.16732).
  `iterative-uncertainty.webp`: Fig. 1, PDF page 1, crop `(306,174,542,325)`
  in PDF points from the top left, 400 dpi. Text covers iterative prediction
  variance, empirical convergence/accuracy relationship, road detection,
  aerodynamic prediction and Bayesian optimization with physical simulations.
  Corrected erroneous arXiv ID 2406.18944; PDF annotations confirm code
  `https://github.com/cvlab-epfl/iter_unc` and project
  `https://www.norange.io/projects/unc_iter/`.
- **IT³: Idempotent Test-Time Training** (ICML 2025):
  [proceedings](https://proceedings.mlr.press/v267/durasov25a.html),
  [PDF](https://proceedings.mlr.press/v267/durasov25a/durasov25a.pdf),
  [author project](https://nikitadurasov.github.io/projects/ittt/).
  `it3-adaptation.webp`: Fig. 1, PDF page 2, crop `(75,72,513,205)` at 400 dpi.
  Explains the trained prediction-conditioning formulation and test-time
  idempotence objective. Does not imply arbitrary unprepared models can use it,
  or that agreement guarantees correctness. Author project verifies arXiv
  **2410.04201**, replacing unrelated ID 2411.17608. Proceedings and PDF verify
  official code `https://github.com/nikitadurasov/ittt`.

## 3D shape

- **PartSDF** (TMLR 2025): [author project](https://ntalabot.github.io/partsdf/),
  [publication](https://openreview.net/forum?id=zl43C1yBKv),
  [arXiv 2502.12985v3](https://arxiv.org/abs/2502.12985v3).
  `partsdf-control.webp`: Fig. 1, arXiv PDF page 2, crop `(72,87,540,183)`
  at 400 dpi. The paper supports per-part latent codes/poses, a shared cross-part
  decoder, supervision from part annotations without watertight part meshes,
  and car-body optimization with wheels fixed. The
  [associated dataset](https://zenodo.org/records/17466765) was already in the
  bibliography and is now tagged `3d` alongside the paper.
- **StyleFields**: [arXiv 2610.09200v1](https://arxiv.org/abs/2610.09200v1),
  public preprint, October 2026. Authors: Ehsan Garaaghaji, Nicolas Talabot,
  Pascal Fua, Doruk Öner. Added as `venue_type=preprint`, not an accepted venue.
  `stylefields-mixing.webp`: Fig. 4, PDF page 7, crop `(169,289,447,377)`.
  `stylefields-optimization.webp`: Fig. 5, PDF page 8, crop `(134,114,481,231)`.
  Both 400 dpi, lossless WebP, full figure panels and labels retained; typeset
  captions excluded in favor of original explanatory captions with attribution.
  Text covers AdaIN-modulated style codes at multiple depths, progressive growth
  and smoothed-target supervision, mixing geometric scales, and selective
  optimization through a drag surrogate. Predicted pressure colors are explained;
  no claim that surrogate optimization alone constitutes physical validation.

## Scope and maintenance

`uncertainty` tags: stochastic nonlinearities, iterative uncertainty, IT³.
`3d` tags: StyleFields, PartSDF, PartSDF dataset. Earlier collaborations are
identified in the introductory copy. No trajectory records, text or images were
changed. StyleFields is ordered after the existing 2026 records so the home
page's latest-publication selection remains unchanged. Narrative text is
editorial; related publication lists are generated solely from CSV tags.
