# Detection Engineering Blueprint

## Sensor placement

Capture 802.11 monitor-mode telemetry near managed access points. Preserve channel, sensor identity, capture timestamp, and deployment context outside the feature vector so they remain available for investigation without becoming model shortcuts.

## Analytic layers

1. **Protocol rules** identify clear management-frame abuse, including abnormal deauthentication and association bursts.
2. **Statistical baselines** compare frame-type rates, signal strength, retry behavior, and protected-frame ratios with each site's normal profile.
3. **Machine-learning scoring** classifies short windows or frames and contributes a confidence score rather than a final incident decision.
4. **Correlation** combines wireless telemetry with access-point logs, RADIUS events, DHCP assignments, and endpoint observations.

## Alert fields

Every alert should include the sensor, BSSID, channel, affected station, time window, model version, score, top contributing fields, matched protocol conditions, and links to retained evidence.

## Validation gates

- Capture-level holdout with no source-file overlap
- Time-based holdout from a later collection period
- Device and location holdout
- Throughput and latency test at expected peak frame rates
- Alert-volume test with analyst review
- Drift monitoring for firmware, channel, hardware, and client-population changes
- Adversarial checks for spoofed signal strength, replay, and malformed frames

## Response mapping

Flooding alerts should trigger availability triage and management-frame review. Impersonation alerts should trigger rogue-access-point validation, credential-exposure checks, and identity-system review. Automated containment should require corroborating evidence to avoid disconnecting legitimate clients on a false positive.
