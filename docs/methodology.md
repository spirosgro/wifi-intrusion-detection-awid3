# Methodology

## Study question

The study asks whether a compact set of IEEE 802.11 frame features can separate Normal, Flooding, and Impersonation traffic, and how classifier choice affects macro performance and execution cost.

## Data scope

The academic result tables use a three-class subset with 12,292,516 reported records: 11,880,478 Normal, 305,876 Flooding, and 106,162 Impersonation. Injection and higher-layer attack classes are outside this experiment.

The official AWID3 corpus covers a broader set of 802.11 and multi-layer attacks. The three-class framing is an assignment-specific analytical choice, not the full AWID3 ontology.

## Feature set

The reference implementation uses the 16 features described in the project's cited feature-selection literature. The feature list is recorded in `data/feature_dictionary.csv`. It combines frame length, radiotap measurements, and IEEE 802.11 frame-control fields.

## Leakage controls

Random packet-level splitting can place near-duplicate frames from the same capture in both training and test data. The included pipeline derives a `source_file` group and uses `GroupShuffleSplit` so a capture appears on only one side of the split.

The pipeline excludes timestamp and frame-number fields from the model. These fields can encode capture identity and chronology rather than transferable attack behavior.

## Evaluation

Primary metric: macro F1. Each class contributes equally to the final score, which prevents the Normal majority from dominating the evaluation.

Supporting outputs include balanced accuracy, macro precision, macro recall, per-class F1, confusion matrices, fit time, and prediction time. Production evaluation should add alert-rate, throughput, latency, drift, and analyst-review metrics.

## Model comparison

The archived presentation compared six tree-based classifiers. The included implementation supports four classifiers from scikit-learn and loads XGBoost or LightGBM when their optional packages are installed.

## Interpretation boundary

The archived numbers show internal offline performance under one reported split design. They do not prove transfer to another site, radio environment, device population, firmware baseline, or live sensor. A deployment claim requires temporal and site-level holdouts, calibration, threshold analysis, and operational validation.
