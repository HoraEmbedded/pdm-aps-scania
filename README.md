# Scania APS — Truck fault triage

[Français](README.fr.md) · [Run the demo](docs/reproduction.md) · [Official test results](reports/test_result.json)

Ten-week academic internship at ENSA Tangier using the Scania APS data published by UCI. The system helps prioritize compressed-air system inspections for trucks already in a workshop. The project covers model comparison, decision threshold selection under asymmetric costs, and deployment through a dashboard and an API.

## Official test-set results

| Metric | Result |
|---|---:|
| APS faults detected | **360 out of 375 (96%)** |
| Missed faults / false alerts | 15 / 387 |
| Model cost / flag-all baseline cost | **11,370 / 156,250 units** |
| Cost reduction against that baseline | **92.72%** |
| Median local single-vehicle inference on Raspberry Pi 4 | **277.13 ms** over 200 calls |

The challenge assigns 500 units to a missed fault and 10 to a false alert. The reported reduction uses those units. Inference latency excludes the network round trip. [Official result](reports/test_result.json) · [Raspberry Pi measurements](reports/deployment_raspberry-pi-4.json)

## Engineering approach

1. **Compare five model families.** The benchmark uses 48,000 vehicles, a separate 12,000-vehicle set is used to compare the finalists, and the 16,000-vehicle official set is used for final evaluation.
2. **Choose an operating point.** The gradient boosting threshold was selected from out-of-fold predictions and frozen before official evaluation. The difference between finalists on the reserved set fell below the predefined margin. Dispersion across repeated runs was used as an additional tie-breaker.
3. **Serve the model.** The Streamlit dashboard accepts a single vehicle or a file and exposes the cost trade-off. The FastAPI service shares the same preprocessing and prediction code. Raspberry Pi 4 deployment includes timing measurements and 21 reference inputs.

## Validation boundaries

The anonymized data contain no longitudinal observations. The evaluation measures workshop triage. Fault lead time and performance under drift still require separate evaluation. The published comparisons found no measurable improvement from the added missingness indicators. The historical benchmark fitted preprocessing on all 48,000 fitting rows before cross-validation. Strictly out-of-fold benchmark estimates would require fitting preprocessing inside each fold. The reserved set and official test set were separate from those 48,000 rows.

## Explore the project

| Find | Start here |
|---|---|
| Run the demo or checks | [Reproduction guide](docs/reproduction.md) |
| Review the protocol and model choice | [Evaluation protocol](docs/evaluation_protocol.md) · [Reserved-set results](reports/arbitration.csv) |
| Inspect the implementation | [Predictor](src/inference.py) · [API](src/api.py) · [Tests](tests/) |
| Verify deployment measurements | [Deployment comparison](reports/deployment_summary.csv) · [Port verification](scripts/check_port.py) |
