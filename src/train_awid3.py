#!/usr/bin/env python3
"""Reference, leakage-aware AWID3 three-class training pipeline.

This implementation supports a fresh experiment on an authorized AWID3 CSV copy.
It does not recreate the undocumented split used by the archived student results.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import yaml
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.tree import DecisionTreeClassifier

ROOT = Path(__file__).resolve().parents[1]

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="CSV file or directory containing AWID3 CSV files")
    parser.add_argument("--model", default="random_forest", choices=[
        "decision_tree", "random_forest", "extra_trees", "hist_gradient_boosting", "xgboost", "lightgbm"
    ])
    parser.add_argument("--config", default=str(ROOT / "config/experiment.yml"))
    parser.add_argument("--output-dir", default=str(ROOT / "runs/reference"))
    parser.add_argument("--max-rows", type=int, default=None, help="Optional total row cap for a development run")
    return parser.parse_args()

def normalize_label(value):
    text = str(value).strip().lower().replace("-", "_").replace(" ", "_")
    if text in {"normal", "benign", "0"}:
        return "Normal"
    if any(token in text for token in ("deauth", "disass", "assoc", "kr00k", "flood")):
        return "Flooding"
    if any(token in text for token in ("rogue", "evil", "krack", "imperson")):
        return "Impersonation"
    return None

def discover_csvs(input_path):
    path = Path(input_path)
    files = [path] if path.is_file() else sorted(path.rglob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No CSV files found under {path}")
    return files

def find_label(columns, candidates):
    for candidate in candidates:
        if candidate in columns:
            return candidate
    raise ValueError(f"No label column found. Tried: {candidates}")

def load_frames(files, config, max_rows):
    frames = []
    remaining = max_rows
    requested = config["continuous_features"] + config["categorical_features"]
    for file in files:
        header = pd.read_csv(file, nrows=0)
        label_name = find_label(header.columns, config["label_candidates"])
        available = [name for name in requested if name in header.columns]
        missing = sorted(set(requested) - set(available))
        if missing:
            raise ValueError(f"{file.name} is missing required features: {missing}")
        nrows = remaining if remaining is not None else None
        frame = pd.read_csv(file, usecols=available + [label_name], nrows=nrows, low_memory=False)
        frame = frame.rename(columns={label_name: "__source_label"})
        frame["source_file"] = file.name
        frames.append(frame)
        if remaining is not None:
            remaining -= len(frame)
            if remaining <= 0:
                break
    data = pd.concat(frames, ignore_index=True)
    data["public_class"] = data["__source_label"].map(normalize_label)
    data = data[data["public_class"].notna()].copy()
    if data.empty:
        raise ValueError("No Normal, Flooding, or Impersonation labels remained after mapping")
    return data

def build_model(name, random_state):
    if name == "decision_tree":
        return DecisionTreeClassifier(max_depth=12, min_samples_leaf=10, class_weight="balanced", random_state=random_state)
    if name == "random_forest":
        return RandomForestClassifier(n_estimators=100, max_depth=12, class_weight="balanced", n_jobs=-1, random_state=random_state)
    if name == "extra_trees":
        return ExtraTreesClassifier(n_estimators=60, max_depth=18, class_weight="balanced", n_jobs=-1, random_state=random_state)
    if name == "hist_gradient_boosting":
        return HistGradientBoostingClassifier(max_iter=120, learning_rate=0.04, random_state=random_state)
    if name == "xgboost":
        try:
            from xgboost import XGBClassifier
        except ImportError as exc:
            raise SystemExit("Install optional package: pip install xgboost") from exc
        return XGBClassifier(n_estimators=120, learning_rate=0.04, reg_lambda=2.0, subsample=0.8, colsample_bytree=0.8, n_jobs=-1, random_state=random_state)
    if name == "lightgbm":
        try:
            from lightgbm import LGBMClassifier
        except ImportError as exc:
            raise SystemExit("Install optional package: pip install lightgbm") from exc
        return LGBMClassifier(n_estimators=120, learning_rate=0.04, num_leaves=20, class_weight="balanced", n_jobs=-1, random_state=random_state)
    raise ValueError(name)

def main():
    args = parse_args()
    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)

    files = discover_csvs(args.input)
    data = load_frames(files, config, args.max_rows)
    features = config["continuous_features"] + config["categorical_features"]

    continuous = Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", MinMaxScaler())])
    categorical = Pipeline([("impute", SimpleImputer(strategy="most_frequent")), ("encode", OneHotEncoder(handle_unknown="ignore", sparse_output=False))])
    preprocessor = ColumnTransformer([
        ("continuous", continuous, config["continuous_features"]),
        ("categorical", categorical, config["categorical_features"]),
    ])
    estimator = build_model(args.model, config["random_state"])
    pipeline = Pipeline([("preprocess", preprocessor), ("model", estimator)])

    splitter = GroupShuffleSplit(n_splits=1, test_size=config["test_size"], random_state=config["random_state"])
    train_index, test_index = next(splitter.split(data[features], data["public_class"], groups=data["source_file"]))
    train, test = data.iloc[train_index], data.iloc[test_index]

    start = time.perf_counter()
    class_to_id = {name: index for index, name in enumerate(config["classes"])}
    id_to_class = {index: name for name, index in class_to_id.items()}
    train_labels = train["public_class"].map(class_to_id)
    pipeline.fit(train[features], train_labels)
    fit_seconds = time.perf_counter() - start
    start = time.perf_counter()
    predicted_ids = pipeline.predict(test[features])
    predicted = np.array([id_to_class[int(value)] for value in predicted_ids])
    predict_seconds = time.perf_counter() - start

    precision, recall, f1, _ = precision_recall_fscore_support(test["public_class"], predicted, average="macro", zero_division=0)
    labels = config["classes"]
    metrics = {
        "model": args.model,
        "records": len(data),
        "train_records": len(train),
        "test_records": len(test),
        "accuracy": accuracy_score(test["public_class"], predicted),
        "balanced_accuracy": balanced_accuracy_score(test["public_class"], predicted),
        "macro_precision": precision,
        "macro_recall": recall,
        "macro_f1": f1,
        "fit_seconds": fit_seconds,
        "predict_seconds": predict_seconds,
        "random_state": config["random_state"],
    }
    (output / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (output / "classification_report.json").write_text(
        json.dumps(classification_report(test["public_class"], predicted, labels=labels, output_dict=True, zero_division=0), indent=2),
        encoding="utf-8",
    )
    pd.DataFrame(confusion_matrix(test["public_class"], predicted, labels=labels), index=labels, columns=labels).to_csv(output / "confusion_matrix.csv")
    pd.DataFrame({"source_file": train["source_file"].drop_duplicates(), "split": "train"}).to_csv(output / "train_groups.csv", index=False)
    pd.DataFrame({"source_file": test["source_file"].drop_duplicates(), "split": "test"}).to_csv(output / "test_groups.csv", index=False)
    joblib.dump(pipeline, output / "model.joblib")
    print(json.dumps(metrics, indent=2))

if __name__ == "__main__":
    main()
