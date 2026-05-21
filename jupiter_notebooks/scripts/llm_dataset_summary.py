#!/usr/bin/env python3
"""
llm_dataset_summary.py
======================
Computes the dataset summary table for Case Study II (Transformer Language Models).

For each of the four models and each of the four weight-matrix types
(attn_input, attn_output, ffn_input, ffn_output) this script reports:

PRIMARY INFO
  n           total number of scalar weight entries
  min / max   observed range of weight values
  missing     count of NaN / Inf values (should be 0)

MARGINAL STATISTICS (pooled across all layers)
  mean        mean weight value
  std         standard deviation
  skew        classical Fisher skewness  (scipy.stats.skew)
  kurt        classical excess kurtosis  (scipy.stats.kurtosis, Fisher=True)

OUTPUT
  - Prints a console summary
  - Writes  llm_dataset_summary.csv  (machine-readable, included in repo)
  - Writes  llm_dataset_summary_table.tex  (LaTeX table ready to paste)

REQUIREMENTS
  pip install transformers torch scipy numpy pandas

MODELS (downloaded automatically from Hugging Face on first run,
        then cached in ~/.cache/huggingface):
  gpt2                     (GPT-2 Small,  124M)
  gpt2-medium              (GPT-2 Medium, 355M)
  facebook/opt-125m        (OPT-125M,     125M)
  EleutherAI/pythia-160m   (Pythia-160M,  160M)
"""

import math
import warnings
import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")


# ── MAD helpers (C-Trapezoid, same formulas as paper) ─────────────────
def empirical_octiles(w: np.ndarray):
    """Return O[1..7] from a weight array (flattened)."""
    return np.quantile(w, [i/8 for i in range(1, 8)])


def c_trap_H(w: np.ndarray) -> float:
    """Compute MAD spread H via C-Trapezoid from a weight array."""
    O1, O2, O3, _, O5, O6, O7 = empirical_octiles(w)
    IL = (3*O1 - 2*O2 + 3*O3) / 8.0
    IR = (3*O5 - 2*O6 + 3*O7) / 8.0
    return float(IR - IL)


# ── Weight extraction ──────────────────────────────────────────────────
def extract_weights(model_id: str):
    """Load model and extract the four canonical weight roles per layer."""
    from transformers import AutoModelForCausalLM
    import torch

    print(f"\nLoading {model_id} ...", flush=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch.float32, low_cpu_mem_usage=True
    )
    model.eval()
    sd = {k: v.detach().float().numpy() for k, v in model.state_dict().items()}
    roles = {r: [] for r in ("attn_input", "attn_output", "ffn_input", "ffn_output")}

    if "gpt2" in model_id.lower():
        for layer in sorted(
            {k.split(".")[2] for k in sd if k.startswith("transformer.h.")}, key=int
        ):
            pf = f"transformer.h.{layer}"
            roles["attn_input"].append(sd[f"{pf}.attn.c_attn.weight"].flatten())
            roles["attn_output"].append(sd[f"{pf}.attn.c_proj.weight"].flatten())
            roles["ffn_input"].append(sd[f"{pf}.mlp.c_fc.weight"].flatten())
            roles["ffn_output"].append(sd[f"{pf}.mlp.c_proj.weight"].flatten())
    elif "opt" in model_id.lower():
        for layer in range(model.config.num_hidden_layers):
            pf = f"model.decoder.layers.{layer}"
            qw = sd[f"{pf}.self_attn.q_proj.weight"]
            kw = sd[f"{pf}.self_attn.k_proj.weight"]
            vw = sd[f"{pf}.self_attn.v_proj.weight"]
            roles["attn_input"].append(np.concatenate([qw.flatten(), kw.flatten(), vw.flatten()]))
            roles["attn_output"].append(sd[f"{pf}.self_attn.out_proj.weight"].flatten())
            roles["ffn_input"].append(sd[f"{pf}.fc1.weight"].flatten())
            roles["ffn_output"].append(sd[f"{pf}.fc2.weight"].flatten())
    elif "pythia" in model_id.lower():
        for layer in range(model.config.num_hidden_layers):
            pf = f"gpt_neox.layers.{layer}"
            roles["attn_input"].append(sd[f"{pf}.attention.query_key_value.weight"].flatten())
            roles["attn_output"].append(sd[f"{pf}.attention.dense.weight"].flatten())
            roles["ffn_input"].append(sd[f"{pf}.mlp.dense_h_to_4h.weight"].flatten())
            roles["ffn_output"].append(sd[f"{pf}.mlp.dense_4h_to_h.weight"].flatten())
    else:
        raise ValueError(f"Unknown model family: {model_id}")

    del model
    return roles


# ── Main ───────────────────────────────────────────────────────────────
MODELS = [
    ("GPT-2 Small",  "gpt2"),
    ("GPT-2 Medium", "gpt2-medium"),
    ("OPT-125M",     "facebook/opt-125m"),
    ("Pythia-160M",  "EleutherAI/pythia-160m"),
]
ROLES = ["attn_input", "attn_output", "ffn_input", "ffn_output"]

records = []

for model_name, model_id in MODELS:
    try:
        roles = extract_weights(model_id)
    except Exception as e:
        print(f"  ERROR loading {model_id}: {e}")
        continue

    for role in ROLES:
        layers  = roles[role]
        all_w   = np.concatenate(layers)

        n       = len(all_w)
        w_min   = float(all_w.min())
        w_max   = float(all_w.max())
        missing = int(np.sum(~np.isfinite(all_w)))
        mean_w  = float(all_w.mean())
        std_w   = float(all_w.std())
        skew_w  = float(stats.skew(all_w))
        kurt_w  = float(stats.kurtosis(all_w, fisher=True))

        records.append(dict(
            model=model_name, role=role, n=n,
            w_min=w_min, w_max=w_max, missing=missing,
            mean=mean_w, std=std_w, skew=skew_w, kurt=kurt_w,
        ))
        fmt_n = f"{n/1e6:.2f}M"
        print(f"  {model_name:<14} {role:<13}  n={fmt_n}  "
              f"mean={mean_w:+.4f}  std={std_w:.4f}  "
              f"skew={skew_w:+.3f}  kurt={kurt_w:+.3f}")

# ── Save ───────────────────────────────────────────────────────────────
df = pd.DataFrame(records)
df.to_csv("llm_dataset_summary.csv", index=False)
print("\nSaved: llm_dataset_summary.csv")
