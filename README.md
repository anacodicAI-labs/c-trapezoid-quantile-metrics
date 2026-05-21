# Elementary and Robust Distribution Shape Analysis via Mean Absolute Deviations and Quantile-Based Quadrature Approximations

**Reproducibility package for the article:**

> Eugene Pinsky, Triparna Kundu, and Rashanjot Kaur  
> *Elementary and Robust Distribution Shape Analysis via Mean Absolute Deviations and Quantile-Based Quadrature Approximations*  
> **Journal of Experimental and Theoretical Analyses (JETA), 2026**  
> DOI: *forthcoming*  
> Department of Computer Science, Boston University Metropolitan College

---

## Abstract

This repository provides the complete computational reproducibility package for the above article. The paper establishes a rigorous connection between quantile-based shape statistics and mean absolute deviations (MAD): it shows that the classical spread ($H$), skewness ($G$), and kurtosis ($K$) of a distribution can be expressed exactly as integrals of the quantile function $Q(p)$ over the unit interval, and proposes a **C-Trapezoid quadrature approximation** that evaluates these integrals from only seven octile values yet achieves substantially lower approximation error than the standard midpoint (IQR-based) rule.

The framework is illustrated on two empirical case studies: (I) twenty-six years of XLK ETF intraday returns (1999–2025), and (II) the weight matrices of four pre-trained transformer language models.

---

## Theoretical Background

### MAD-based shape metrics

For a distribution with quantile function $Q(p)$, define the left and right subareas

$$I_L = \int_0^{1/2} Q(p)\,dp, \qquad I_R = \int_{1/2}^{1} Q(p)\,dp.$$

The three shape metrics are

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| Spread | $H = I_R - I_L$ | Median absolute deviation |
| Skewness | $G = \dfrac{(I_L+I_R) - O_4}{H}$ | Normalized distance of mean from median |
| Kurtosis | $K = \dfrac{I_{LR}-I_{LL}+I_{RR}-I_{RL}}{H}$ | Relative concentration in the tails |

where $O_4 = Q(1/2)$ is the median and $I_{LL},I_{LR},I_{RL},I_{RR}$ are the quarter-subareas.

### C-Trapezoid approximation

Using only the seven octiles $O_i = Q(i/8),\ i=1,\ldots,7$:

$$\hat I_L = \frac{3O_1 - 2O_2 + 3O_3}{8}, \qquad \hat I_R = \frac{3O_5 - 2O_6 + 3O_7}{8}$$

$$\hat H = \hat I_R - \hat I_L, \qquad \hat G = \frac{(\hat I_L + \hat I_R) - O_4}{\hat H}$$

$$\hat K = \frac{3(O_7-O_1) - 3(O_6-O_2) + (O_5-O_3)}{3(O_7-O_1) - 2(O_6-O_2) + 3(O_5-O_3)}$$

The coefficients arise from cubic-polynomial endpoint extrapolation combined with the composite trapezoid rule, and reduce algebraically to the compact closed forms above.

### Connection to L-moments

A key theoretical result (proved in the paper) is

$$l_2 = \tfrac{1}{2} \int_0^1 H(X,\,Q(p))\,dp,$$

showing that the second L-moment equals half the mean MAD over all quantile levels. The C-Trapezoid estimates $\hat H$ are thus lightweight, non-iterative approximations to the same quantity that L-moments measure exactly.

---

## Repository Structure

```
c-trapezoid-quantile-metrics/
│
├── README.md                            ← this file
├── requirements.txt                     ← Python dependencies
│
├── comparison_approximations.ipynb      ← §3–4  Quadrature accuracy across distributions
├── simple_h_approximation_comparisons_11_17_2025_laplace_fixed.ipynb
│                                        ← §10   XLK case study main analysis notebook
│
├── jupiter_notebooks/scripts/           ← Standalone replication scripts
│   ├── wall_clock_mle_vs_closed_form.py ← §8    Table 9: MLE vs closed-form timing
│   ├── wall_clock_mle_vs_closed_form.csv←        Pre-computed timing results
│   ├── llm_dataset_summary.py           ← §11   Table 26: LLM dataset statistics
│   ├── llm_dataset_summary.csv          ←        Pre-computed results
│   ├── llm_weight_acf.py                ← §11   Table 27: raw weight autocorrelation
│   └── llm_weight_acf.csv              ←        Pre-computed results
│
├── figures_llm/                         ← §11   All paper figures for Case Study II
│   ├── llm_fig1_histograms.png          ← Fig. 12  Weight histograms by layer
│   ├── llm_fig2_H_vs_depth.png          ← Fig. 16  Spread H vs. layer depth
│   ├── llm_fig3_K_vs_depth.png          ← Fig. 17  Kurtosis K vs. layer depth
│   ├── llm_fig4_gpt2_three_methods.png  ← Fig. 15  GPT-2 Small: exact/C-Trap/midpoint
│   ├── llm_fig5_gpt2_scaling.png        ← Fig. 19  GPT-2 Small vs. Medium scaling
│   ├── llm_fig6_cross_family.png        ← Fig. 20  Cross-family comparison
│   ├── llm_fig7_boxplots.png            ← Fig. 18  Boxplots by weight role
│   ├── llm_fig_scatter_H_parallel.png   ← Fig. 13  Scatter: exact vs. approx H
│   └── llm_fig_scatter_K_parallel.png   ← Fig. 14  Scatter: exact vs. approx K
│
├── case_study_llm/                      ← §11   Notebooks for Case Study II
│   ├── nb1-ctrapezoid/                  ←        C-Trapezoid + Midpoint computation
│   │   ├── nb1_ctrapezoid.ipynb
│   │   ├── all_ctrap.csv               ←        Per-layer H, G, K (all models)
│   │   └── summary_ctrap.csv
│   ├── nb2-exact/                       ←        Exact (full-sort) baseline
│   │   ├── nb2_exact.ipynb
│   │   ├── all_exact.csv               ←        Per-layer exact H, G, K
│   │   └── summary_exact.csv
│   └── nb3-comparison/                  ←        All-methods comparison + figures
│       ├── nb3_comparison.ipynb
│       ├── all_compare.csv
│       ├── error_summary.csv           ←        Table 31: percentage errors
│       └── gpt2_small_comparison.csv
│
└── case_study_stock/                    ← §10   Case Study I: XLK ETF
    ├── jupiter_notebooks/               ←        Analysis notebooks
    ├── XLK_line_H.jpg                  ←        Fig. 6a  H spread over time
    ├── XLK_line_O4H.jpg                ←        Fig. 6b  O₄/H ratio over time
    ├── XLK_boxplot_H.jpg               ←        Boxplot distributions of H
    ├── XLK_boxplot_O4H.jpg
    ├── XLK_line_G.jpg                  ←        Skewness G over time
    ├── XLK_line_K.jpg                  ←        Kurtosis K over time
    ├── XLK_boxplot_G.jpg
    ├── XLK_boxplot_K.jpg
    ├── XLK_MAD_pct_err_CO.jpg          ←        Fig. 5a  MAD % error (overnight)
    └── XLK_MAD_pct_err_OC.jpg         ←        Fig. 5b  MAD % error (daytime)
```

---

## Quick Start

```bash
git clone https://github.com/anacodicAI-labs/c-trapezoid-quantile-metrics.git
cd c-trapezoid-quantile-metrics
pip install -r requirements.txt
```

---

## Standalone Replication Scripts

Each script is self-contained, writes outputs to the current working directory, and reproduces a specific table in the paper. Pre-computed results (CSV files) are included for readers who do not wish to re-run computations.

---

### `wall_clock_mle_vs_closed_form.py` — Paper Table 9

**What it measures.** Median wall-clock time (milliseconds) for two Weibull parameter-estimation strategies across sample sizes $n \in \{100, 10^3, 10^4, 10^5\}$:

- **MLE** — iterative optimization via `scipy.stats.weibull_min.fit` with `floc=0`
- **Closed-form** — non-iterative PWM / L-moment inversion: sort once, compute two probability-weighted moments, apply the algebraic formulae $\hat\alpha = -\ln 2\,/\,\ln(1 - \hat\tau_2)$ and $\hat\beta = \hat l_1\,/\,\Gamma(1 + 1/\hat\alpha)$

**Usage.**
```bash
cd jupiter_notebooks/scripts
python wall_clock_mle_vs_closed_form.py
# writes wall_clock_mle_vs_closed_form.csv
```

**Paper result (Table 9, one representative workstation).**

| $n$ | MLE (ms) | Closed-Form (ms) | Time Saved vs MLE |
|-----|----------|-----------------|-------------------|
| 100 | 1.66 | 0.038 | **97.7 %** |
| 1,000 | 2.25 | 0.361 | **83.9 %** |
| 10,000 | 10.54 | 3.62 | **65.6 %** |
| 100,000 | 99.54 | 36.85 | **63.0 %** |

> **Note:** timings are hardware-dependent. Re-run the script on your machine for reproducible values; the closed-form method consistently dominates MLE by 1–2 orders of magnitude at small $n$.

---

### `llm_dataset_summary.py` — Paper Table 26

**What it computes.** Primary information and marginal statistics for the weight matrices of four pre-trained transformer models:

| Statistic | Description |
|-----------|-------------|
| $n$ | Total scalar weight entries (architecture-exact) |
| $[\min, \max]$ | Observed range |
| Missing | Count of non-finite entries (0 for all models) |
| Mean | Pooled mean across all layers |
| Std | Pooled standard deviation |
| $G_c$ | Classical (Fisher) skewness |
| $K_c^{\text{ex}}$ | Classical excess kurtosis |

**Usage.**
```bash
cd jupiter_notebooks/scripts
python llm_dataset_summary.py
# writes llm_dataset_summary.csv
# models are downloaded automatically (~2 GB, cached after first run)
```

Pre-computed results: `llm_dataset_summary.csv`.

**Key finding:** All weight distributions are leptokurtic ($K_c^{\text{ex}} > 0$), with pooled means within $10^{-3}$ of zero — consistent with near-zero-mean initialisation and gradient-based training.

---

### `llm_weight_acf.py` — Paper Table 27

**What it computes.** Mean Pearson autocorrelation of raw weight values at lags 1–5. For each model, weight-matrix role, and layer, the weight matrix is flattened into a one-dimensional vector; ACF is computed and averaged across layers.

**Usage.**
```bash
cd jupiter_notebooks/scripts
python llm_weight_acf.py
# writes llm_weight_acf.csv
```

Pre-computed results: `llm_weight_acf.csv`.

**Key finding:** All autocorrelation values lie within $\pm 0.03$ of zero, confirming that scalar weight entries are approximately uncorrelated within each matrix, consistent with near-i.i.d. initialisation. The sole exception is `ffn_input` for GPT-2 Small (${\approx}{+}0.022$) and GPT-2 Medium (${\approx}{+}0.026$), where a small but uniform positive ACF persists across all five lags.

---

## Case Study I — XLK ETF Intraday Returns (1999–2025)

### Data

The **Technology Select Sector SPDR Fund (XLK)** provides daily open, high, low, and close prices. Two non-overlapping return series are constructed for each trading day:

| Series | Definition | Regime |
|--------|-----------|--------|
| **Overnight (CO)** | $\ln(\text{Open}/\text{Close}_{\text{prev}})$ | Off-exchange hours |
| **Daytime (OC)** | $\ln(\text{Close}/\text{Open})$ | Regular trading hours |

For each calendar year the sample contains approximately 250 observations. Octiles are estimated empirically and used to compute $\hat H$, $\hat G$, $\hat K$, and $O_4/H$ via both the midpoint and C-Trapezoid approximations; exact values serve as the reference.

### Key Findings

- C-Trapezoid approximation errors are **2–3× lower** than midpoint errors for $H$ in both return series.
- The **overnight** series exhibits materially higher spread and excess kurtosis than the daytime series, reflecting the information-accumulation dynamics of off-market hours.
- $H$ and $K$ exhibit pronounced **temporal structure**: they spike in 2000–2002 (dot-com collapse), 2008–2009 (financial crisis), 2020 (COVID-19 shock), and 2022 (rate-hike cycle).
- $O_4/H$ — the normalized median return — identifies directionality; it is persistently positive during bull markets and reverses sharply in bear years.

### Main Notebook

`simple_h_approximation_comparisons_11_17_2025_laplace_fixed.ipynb` — generates all XLK figures.

### Selected Figures

| | |
|:---:|:---:|
| ![MAD % err CO](case_study_stock/XLK_MAD_pct_err_CO.jpg) | ![MAD % err OC](case_study_stock/XLK_MAD_pct_err_OC.jpg) |
| **Fig. 5a** Approximation error — overnight | **Fig. 5b** Approximation error — daytime |
| ![H line](case_study_stock/XLK_line_H.jpg) | ![K line](case_study_stock/XLK_line_K.jpg) |
| **Fig. 6a** Spread $H$ over time | Kurtosis $K$ over time |

---

## Case Study II — Transformer Language-Model Weight Distributions

### Models

| Model | Family | Parameters | Layers | Source |
|-------|--------|-----------|--------|--------|
| GPT-2 Small | GPT-2 | 117 M | 12 | [Radford et al., 2019](https://openai.com/research/language-models-are-unsupervised-multitask-learners) |
| GPT-2 Medium | GPT-2 | 345 M | 24 | [Radford et al., 2019](https://openai.com/research/language-models-are-unsupervised-multitask-learners) |
| OPT-125M | OPT | 125 M | 12 | [Zhang et al., 2022](https://arxiv.org/abs/2205.01068) |
| Pythia-160M | Pythia | 160 M | 12 | [Biderman et al., 2023](https://arxiv.org/abs/2304.01373) |

For each model, four weight-matrix roles are analysed per layer:

| Role | Weight matrix |
|------|--------------|
| `attn_input` | Combined Q/K/V projection |
| `attn_output` | Attention output projection |
| `ffn_input` | Feed-forward network first layer |
| `ffn_output` | Feed-forward network second layer |

### Methodology

Three computation variants are compared for each weight matrix:

1. **Exact** — full sort of all matrix elements; numerically exact octiles → exact $H$, $G$, $K$
2. **C-Trapezoid** — octile-based approximation using the closed-form formulae above
3. **Midpoint** — IQR-based approximation ($\hat H = (O_6 - O_2)/2$, analogous to midpoint quadrature)

### Key Findings

- **C-Trapezoid outperforms Midpoint** on $H$ by a factor of 3–4× in mean absolute relative error across all four model families.
- **All weight distributions are leptokurtic**: classical excess kurtosis is positive for every role, ranging from $+1.4$ (GPT-2 Medium `ffn_input`) to $+101.6$ (GPT-2 Medium `attn_output`).
- **Depth trends**: `ffn_output` spread $H$ grows monotonically with layer depth in GPT-2 and Pythia; `attn_output` spread shows moderate monotone growth; input roles stabilise quickly after an initial transient at layer 0.
- **Raw weight autocorrelation** at lags 1–5 is near zero for all roles, confirming approximately i.i.d. weight structure within each matrix.
- **Cross-family consistency**: the accuracy ranking Exact > C-Trapezoid > Midpoint holds universally across all models and roles tested.

### Reproducing the Notebooks

Run notebooks in order:

```bash
jupyter lab
# 1. case_study_llm/nb1-ctrapezoid/nb1_ctrapezoid.ipynb
# 2. case_study_llm/nb2-exact/nb2_exact.ipynb
# 3. case_study_llm/nb3-comparison/nb3_comparison.ipynb
```

nb3 reads outputs from nb1 and nb2, so the order is required.
Model weights (~2 GB) are downloaded automatically from [Hugging Face](https://huggingface.co) on first run and cached in `~/.cache/huggingface`.

### Pre-computed Data Files

| File | Description |
|------|-------------|
| `case_study_llm/nb1-ctrapezoid/all_ctrap.csv` | Per-layer C-Trapezoid and Midpoint $H$, $G$, $K$ for all four models |
| `case_study_llm/nb1-ctrapezoid/summary_ctrap.csv` | Per-model mean and standard deviation across layers |
| `case_study_llm/nb2-exact/all_exact.csv` | Per-layer exact $H$, $G$, $K$ |
| `case_study_llm/nb2-exact/summary_exact.csv` | Per-model exact summary |
| `case_study_llm/nb3-comparison/all_compare.csv` | Merged exact + approximation results |
| `case_study_llm/nb3-comparison/error_summary.csv` | Absolute relative errors by model and weight role |
| `case_study_llm/nb3-comparison/gpt2_small_comparison.csv` | Layer-by-layer comparison for GPT-2 Small |
| `jupiter_notebooks/scripts/llm_dataset_summary.csv` | Marginal statistics (Table 26) |
| `jupiter_notebooks/scripts/llm_weight_acf.csv` | Raw weight ACF (Table 27) |

### Selected Figures

| | |
|:---:|:---:|
| ![fig1](figures_llm/llm_fig1_histograms.png) | ![fig4](figures_llm/llm_fig4_gpt2_three_methods.png) |
| **Fig. 12** Weight distributions by layer depth | **Fig. 15** GPT-2 Small: all three methods |
| ![fig2](figures_llm/llm_fig2_H_vs_depth.png) | ![fig3](figures_llm/llm_fig3_K_vs_depth.png) |
| **Fig. 16** Spread $H$ vs. layer depth | **Fig. 17** Kurtosis $K$ vs. layer depth |
| ![fig_H](figures_llm/llm_fig_scatter_H_parallel.png) | ![fig_K](figures_llm/llm_fig_scatter_K_parallel.png) |
| **Fig. 13** Exact vs. approx $H$ (all models) | **Fig. 14** Exact vs. approx $K$ (all models) |
| ![fig6](figures_llm/llm_fig6_cross_family.png) | ![fig5](figures_llm/llm_fig5_gpt2_scaling.png) |
| **Fig. 20** Cross-family comparison | **Fig. 19** GPT-2 scaling (Small vs. Medium) |

---

## Software Environment

```
Python         3.11+
numpy          ≥ 1.24
scipy          ≥ 1.10
pandas         ≥ 2.0
matplotlib     ≥ 3.7
jupyter        ≥ 1.0
transformers   ≥ 4.35   (Case Study II only)
torch          ≥ 2.0    (Case Study II only)
```

Install all dependencies:
```bash
pip install -r requirements.txt
```

---

## Data Availability

All code and pre-computed results are available at:

> [https://github.com/anacodicAI-labs/c-trapezoid-quantile-metrics](https://github.com/anacodicAI-labs/c-trapezoid-quantile-metrics)

The XLK ETF return data used in Case Study I are derived from publicly available daily price data (e.g., Yahoo Finance, WRDS).  
The language-model weights used in Case Study II are loaded directly from the [Hugging Face Hub](https://huggingface.co) under their respective open licences (MIT for GPT-2; OPT licence for OPT-125M; Apache 2.0 for Pythia-160M).

---

## Citation

If you use this code, data, or the methods described in the paper, please cite:

```bibtex
@article{pinsky2026mad,
  title   = {Elementary and Robust Distribution Shape Analysis via Mean Absolute
             Deviations and Quantile-Based Quadrature Approximations},
  author  = {Pinsky, Eugene and Kundu, Triparna and Kaur, Rashanjot},
  journal = {Journal of Experimental and Theoretical Analyses},
  year    = {2026},
  note    = {DOI: forthcoming}
}
```

---

## Acknowledgements

We thank the Department of Computer Science at Boston University Metropolitan College for their support.

---

*Repository maintained by the authors. Issues and pull requests are welcome.*
