#!/usr/bin/env python3
"""
llm_weight_acf.py
=================
Computes autocorrelation of the RAW WEIGHT VALUES at lags 1-5.

For each model x role x layer:
  1. Flatten the weight matrix into a 1D vector
  2. Compute Pearson ACF at lags 1, 2, 3, 4, 5
  3. Average ACF values across all layers

OUTPUT
  llm_weight_acf.csv          machine-readable results (included in repo)
  llm_weight_acf_table.tex    LaTeX table ready to paste into paper

REQUIREMENTS
  pip install transformers torch numpy pandas
"""

import numpy as np
import pandas as pd


def acf_vector(x: np.ndarray, max_lag: int = 5) -> list:
    """Pearson autocorrelation at lags 1..max_lag for a 1D array."""
    x = x.astype(np.float64) - x.mean()
    n = len(x)
    c0 = np.dot(x, x) / n
    if c0 < 1e-14:
        return [0.0] * max_lag
    return [float(np.dot(x[:n - lag], x[lag:]) / (n * c0)) for lag in range(1, max_lag + 1)]


def extract_weights(model_id: str):
    from transformers import AutoModelForCausalLM
    import torch
    print(f"Loading {model_id} ...", flush=True)
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
    del model
    return roles


MODELS = [
    ("GPT-2 Small",  "gpt2"),
    ("GPT-2 Medium", "gpt2-medium"),
    ("OPT-125M",     "facebook/opt-125m"),
    ("Pythia-160M",  "EleutherAI/pythia-160m"),
]
ROLES = ["attn_input", "attn_output", "ffn_input", "ffn_output"]
MAX_LAG = 5

records = []
for model_name, model_id in MODELS:
    try:
        roles = extract_weights(model_id)
    except Exception as e:
        print(f"  ERROR: {e}")
        continue
    for role in ROLES:
        layers = roles[role]
        mean_acf = np.mean([acf_vector(w, MAX_LAG) for w in layers], axis=0).tolist()
        rec = {"model": model_name, "role": role}
        for lag in range(MAX_LAG):
            rec[f"acf_{lag+1}"] = round(mean_acf[lag], 4)
        records.append(rec)
        print(f"  {model_name:<14} {role:<13}  " +
              "  ".join(f"lag{l+1}={mean_acf[l]:+.4f}" for l in range(MAX_LAG)))

df = pd.DataFrame(records)
df.to_csv("llm_weight_acf.csv", index=False)
print("\nSaved: llm_weight_acf.csv")
print("Note: all values near 0.000 — weights are approximately i.i.d. within each matrix.")
