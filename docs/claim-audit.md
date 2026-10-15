# Public Claim Audit

This audit records material corrections made while converting the classroom presentation into a public portfolio project.

| Original framing | Public treatment | Reason |
| --- | --- | --- |
| F1 values converted directly into missed attacks per 1,000 | Removed | F1 combines precision and recall and cannot determine a miss count by itself |
| Training time used to support real-time IDS suitability | Reframed as offline fit cost | Training time does not measure packet-processing latency or throughput |
| XGBoost described as ready for practical deployment | Reframed as the strongest reported offline macro F1 | Deployment requires external validation, calibration, telemetry engineering, and operations testing |
| Machine learning described as detecting unknown attacks by default | Reframed as a hypothesis that requires leave-attack-out or external evaluation | Supervised performance on known labels does not establish zero-day detection |
| 98%+ scores described as independently proven | Labeled as reported academic results | Original data, code, models, split manifest, and logs were not found |
| Feature importance treated as causal explanation | Reframed as model-specific association | Tree importance can reflect correlation, cardinality, and capture artifacts |
| AWID3 reduced to three classes | Clearly labeled as an assignment-specific subset | The official corpus contains a broader attack taxonomy |

## Remaining uncertainty

The reported class-level F1 values reproduce the aggregate macro F1 values after rounding. Selected confusion counts cannot be fully audited without the test-set class totals and prediction export. They remain in the archive as reported values and are not used to derive additional claims.
