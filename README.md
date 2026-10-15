# Wi-Fi Intrusion Detection with AWID3

![Repository cover](assets/repo-cover.png)

An English, claim-audited portfolio edition of an academic Wi-Fi intrusion-detection study. The project examines a three-class AWID3 subset, compares six tree-based classifiers, and translates the findings into a practical detection-engineering design.

## What this repository demonstrates

- Threat analysis for IEEE 802.11ac enterprise networks
- Leakage-aware evaluation with capture-level grouping
- Class-imbalance handling with macro metrics
- Comparison of Decision Tree, Random Forest, Extra Trees, XGBoost, LightGBM, and HistGradientBoosting
- A reusable training pipeline for the public AWID3 CSV release
- Security interpretation that separates measured results from deployment recommendations

## Evidence status

| Item | Status | Meaning |
| --- | --- | --- |
| Academic result tables | Preserved | Transcribed from the original team presentation |
| Result arithmetic | Checked | Macro F1 values are recomputed from class-level F1 scores |
| Original raw dataset | Not included | AWID3 access remains subject to the dataset provider's process |
| Original training notebook | Not found | The exact experiment cannot be independently reproduced from the files discovered on this computer |
| Reference training pipeline | Included | A clean implementation is provided for rerunning the design on an authorized AWID3 copy |
| Production readiness | Not claimed | Reported offline scores do not establish live detection performance |

## Reported findings

The archived experiment reports macro F1 scores from **98.19% to 98.74%**. XGBoost has the highest reported macro F1 at **98.74%**, while Decision Tree reaches **98.34%** with the shortest reported training time. Impersonation traffic is the most variable class across the compared models.

These values are treated as **reported academic results**. They have passed consistency checks against the class-level table, but the original dataset snapshot, split manifest, trained models, and execution logs were not available for independent reproduction.

## Quick start

Validate the archived result tables without downloading AWID3:

```bash
python src/validate_reported_results.py
```

Run a fresh experiment after obtaining AWID3 from the dataset owner:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python src/train_awid3.py --input "path/to/awid3/csv" --model random_forest --max-rows 500000
```

The pipeline groups the train/test split by source file to reduce capture-level leakage. It does not promise bit-for-bit reproduction of the archived experiment because the original preprocessing code and split manifest are unavailable.

## Repository map

```text
assets/                 Repository cover
config/                 Experiment configuration
data/                    Attack taxonomy, feature dictionary, and reported results
docs/                    Method, claim audit, data access, and reproducibility notes
presentation/            English presentation deck
report/                  English technical report
src/                     Validation and reference training code
```

## Research integrity

The public edition corrects several claims from the classroom deck. It does not infer missed-attack counts from F1 alone, does not equate training time with real-time inference, and does not call an offline classifier deployment-ready. See [Claim audit](docs/claim-audit.md) for the complete record.

## Provenance

The original Greek presentation was collaborative university coursework prepared by Spiros Grouztidis and two classmates. The classmates' names and student identifiers are omitted from this public edition for privacy. Spiros Grouztidis prepared this portfolio edition, including the English rewrite, public documentation, reusable code, and detection-engineering extensions.

## Data and third-party material

The AWID3 dataset and the associated research papers are not redistributed here. Request dataset access through the [official AWID project](https://icsdweb.aegean.gr/awid/). The principal dataset paper is [Empirical Evaluation of Attacks Against IEEE 802.11 Enterprise Networks: The AWID3 Dataset](https://doi.org/10.1109/ACCESS.2021.3061609).

## License

Code under `src/` is available under the MIT License. The report, presentation, result transcriptions, and original coursework-derived material remain all rights reserved. See [LICENSE.md](LICENSE.md).
