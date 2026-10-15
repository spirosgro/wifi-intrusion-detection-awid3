# Reproducibility Record

## Available evidence

- The final Greek presentation with dataset counts, model settings, aggregate metrics, class-level F1 scores, and selected confusion counts
- The AWID3 dataset paper used as background material
- Public documentation for the AWID3 corpus

## Missing evidence

- Original AWID3 CSV or PCAP files used by the student team
- Training notebook or source code
- Package versions and hardware details beyond the statement that training used one CPU core
- Random seed, exact group allocation, and split manifest
- Saved models, logs, predictions, and feature-importance exports

## Consequence

The tables in `data/results` are archival transcriptions, not independently reproduced benchmarks. `src/validate_reported_results.py` checks arithmetic consistency. `src/train_awid3.py` provides a new reference implementation for a fresh run but cannot recreate an undocumented split.

## Reproduction checklist

1. Obtain AWID3 from the official project and retain the provider's original file names.
2. Record file hashes and the dataset release date.
3. Confirm feature names and label values against `data/feature_dictionary.csv`.
4. Run the reference pipeline with an explicit model and random seed.
5. Commit the generated split manifest, environment lock file, metrics JSON, class report, and confusion matrix.
6. Compare the new results with the archived tables without overwriting them.
7. Add a second evaluation using unseen capture dates or a different physical environment.
