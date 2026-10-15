#!/usr/bin/env python3
"""Validate internal consistency of the archived AWID3 result tables."""

from pathlib import Path
import csv
import math

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))

overall = {row["model"]: row for row in load(ROOT / "data/results/model_metrics.csv")}
by_class = {row["model"]: row for row in load(ROOT / "data/results/class_f1.csv")}

errors = []
for model, row in overall.items():
    if model not in by_class:
        errors.append(f"{model}: missing class-level row")
        continue
    class_row = by_class[model]
    values = [
        float(class_row["flooding_f1_percent"]),
        float(class_row["impersonation_f1_percent"]),
        float(class_row["normal_f1_percent"]),
    ]
    calculated = sum(values) / len(values)
    reported = float(row["macro_f1_percent"])
    if not math.isclose(calculated, reported, abs_tol=0.011):
        errors.append(
            f"{model}: class mean {calculated:.4f} does not match reported {reported:.2f}"
        )

if errors:
    raise SystemExit("\n".join(errors))

best = max(overall.values(), key=lambda row: float(row["macro_f1_percent"]))
print(f"Validated {len(overall)} models.")
print("All reported macro F1 values match the mean of the three class-level F1 values after rounding.")
print(f"Highest reported macro F1: {best['model']} at {best['macro_f1_percent']}%.")
print("Validation checks arithmetic only; it does not reproduce model training.")
