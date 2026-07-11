"""srlib.metrics — deterministic agreement & promotion-gate metrics.

Pure standard library. Every statistic in Phase 5c is computed HERE by code,
never by any language model (v7 invariant: the code computes).

Conventions (mirror Phase 5a):
- 3-category labels: INCLUDE / EXCLUDE / UNCERTAIN
- binary retain/discard: retain = INCLUDE or UNCERTAIN; discard = EXCLUDE
- "dangerous cell" = model-discard / human-retain (potential missed include)
"""
from __future__ import annotations

import math
import random
from typing import Dict, List, Sequence, Tuple

LABELS3 = ("INCLUDE", "EXCLUDE", "UNCERTAIN")


def to_retain(label: str) -> str:
    return "RETAIN" if label in ("INCLUDE", "UNCERTAIN") else "DISCARD"


def confusion(y_true: Sequence[str], y_pred: Sequence[str],
              labels: Sequence[str]) -> List[List[int]]:
    idx = {l: i for i, l in enumerate(labels)}
    m = [[0] * len(labels) for _ in labels]
    for t, p in zip(y_true, y_pred):
        m[idx[t]][idx[p]] += 1
    return m


def percent_agreement(y_true: Sequence[str], y_pred: Sequence[str]) -> float:
    n = len(y_true)
    return sum(1 for t, p in zip(y_true, y_pred) if t == p) / n if n else float("nan")


def cohen_kappa(y_true: Sequence[str], y_pred: Sequence[str],
                labels: Sequence[str]) -> float:
    n = len(y_true)
    if n == 0:
        return float("nan")
    m = confusion(y_true, y_pred, labels)
    po = sum(m[i][i] for i in range(len(labels))) / n
    pe = sum((sum(m[i]) / n) * (sum(r[i] for r in m) / n) for i in range(len(labels)))
    return float("nan") if pe == 1.0 else (po - pe) / (1 - pe)


def pabak(y_true: Sequence[str], y_pred: Sequence[str], k: int) -> float:
    po = percent_agreement(y_true, y_pred)
    return (k * po - 1) / (k - 1)


def sens_spec(y_true_bin: Sequence[str], y_pred_bin: Sequence[str]
              ) -> Dict[str, float]:
    """Retain/discard sensitivity & specificity. Positive class = RETAIN
    (a retained record survives to full text; missing one is the dangerous error)."""
    tp = sum(1 for t, p in zip(y_true_bin, y_pred_bin) if t == "RETAIN" and p == "RETAIN")
    fn = sum(1 for t, p in zip(y_true_bin, y_pred_bin) if t == "RETAIN" and p == "DISCARD")
    tn = sum(1 for t, p in zip(y_true_bin, y_pred_bin) if t == "DISCARD" and p == "DISCARD")
    fp = sum(1 for t, p in zip(y_true_bin, y_pred_bin) if t == "DISCARD" and p == "RETAIN")
    sens = tp / (tp + fn) if (tp + fn) else float("nan")
    spec = tn / (tn + fp) if (tn + fp) else float("nan")
    return {"tp": tp, "fn": fn, "tn": tn, "fp": fp,
            "sensitivity": sens, "specificity": spec,
            "n_retain_truth": tp + fn, "n_discard_truth": tn + fp}


def wilson_ci(k: int, n: int, z: float = 1.959964) -> Tuple[float, float]:
    """Wilson 95% score interval for a proportion — honest at small n."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = (z / denom) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, centre - half), min(1.0, centre + half))


def mcnemar_exact(b: int, c: int) -> float:
    """Exact two-sided McNemar p-value on discordant pairs (binomial, p=0.5).

    b = incumbent-correct / candidate-wrong; c = incumbent-wrong / candidate-correct.
    Appropriate at pilot scale where the asymptotic chi-square is not.
    """
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def bootstrap_diff_ci(correct_a: Sequence[int], correct_b: Sequence[int],
                      mask: Sequence[int], seed: int, reps: int = 2000
                      ) -> Tuple[float, float]:
    """Seeded paired bootstrap 95% CI for (sens_B − sens_A) over records where
    mask==1 (human-RETAIN records). Descriptive at small n — caller must print
    the caveat. correct_* are 0/1 per record (model retained a human-retain)."""
    rng = random.Random(seed)
    idx = [i for i, m in enumerate(mask) if m == 1]
    if not idx:
        return (float("nan"), float("nan"))
    diffs = []
    for _ in range(reps):
        sample = [idx[rng.randrange(len(idx))] for _ in idx]
        sa = sum(correct_a[i] for i in sample) / len(sample)
        sb = sum(correct_b[i] for i in sample) / len(sample)
        diffs.append(sb - sa)
    diffs.sort()
    lo = diffs[max(0, int(0.025 * reps) - 1)]
    hi = diffs[min(reps - 1, int(0.975 * reps))]
    return (lo, hi)


def directional_table(y_true: Sequence[str], y_pred: Sequence[str]
                      ) -> Dict[str, int]:
    """Binary directional disagreement counts; the dangerous cell first."""
    tb = [to_retain(t) for t in y_true]
    pb = [to_retain(p) for p in y_pred]
    return {
        "model_discard_human_retain__DANGEROUS": sum(
            1 for t, p in zip(tb, pb) if t == "RETAIN" and p == "DISCARD"),
        "model_retain_human_discard": sum(
            1 for t, p in zip(tb, pb) if t == "DISCARD" and p == "RETAIN"),
        "agree_retain": sum(1 for t, p in zip(tb, pb) if t == p == "RETAIN"),
        "agree_discard": sum(1 for t, p in zip(tb, pb) if t == p == "DISCARD"),
    }


def full_panel(y_true: Sequence[str], y_pred: Sequence[str]) -> Dict:
    """The Phase 5a metric discipline in one call: κ ×2, % agreement ×2,
    PABAK ×2, confusion tables, sens/spec with Wilson CIs, directional table."""
    tb = [to_retain(t) for t in y_true]
    pb = [to_retain(p) for p in y_pred]
    ss = sens_spec(tb, pb)
    sens_ci = wilson_ci(ss["tp"], ss["tp"] + ss["fn"]) if (ss["tp"] + ss["fn"]) else (float("nan"),) * 2
    spec_ci = wilson_ci(ss["tn"], ss["tn"] + ss["fp"]) if (ss["tn"] + ss["fp"]) else (float("nan"),) * 2
    return {
        "n": len(y_true),
        "kappa_3cat": cohen_kappa(y_true, y_pred, LABELS3),
        "kappa_binary": cohen_kappa(tb, pb, ("RETAIN", "DISCARD")),
        "pct_agreement_3cat": percent_agreement(y_true, y_pred),
        "pct_agreement_binary": percent_agreement(tb, pb),
        "pabak_3cat": pabak(y_true, y_pred, 3),
        "pabak_binary": pabak(tb, pb, 2),
        "confusion_3cat": confusion(y_true, y_pred, LABELS3),
        "confusion_binary": confusion(tb, pb, ("RETAIN", "DISCARD")),
        "directional": directional_table(y_true, y_pred),
        **ss,
        "sensitivity_wilson95": sens_ci,
        "specificity_wilson95": spec_ci,
    }
