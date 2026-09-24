# Predictive maintenance on the Scania APS dataset

Cost-sensitive failure classification on the air pressure system of Scania trucks. Five model families compared under a protocol frozen before the first training run. Single opening of the official test set.

Fourth-year engineering project, 10 weeks, supervised. French version: [README.fr.md](README.fr.md).

## Description

This work compares five families of classification models for detecting air pressure system (APS) failures in heavy trucks. Industrial data released by Scania in 2016.

The protocol was written, dated and frozen before the first training run. The official test set was opened only once, on a model already frozen, decision threshold included.

## Problem

Trucks in this dataset are already in the workshop. The question is not whether a truck is broken, but whether the failure comes from the air pressure system (APS) or from another component.

Three properties drive every design decision:

| Property | Measured value |
|---|---|
| Imbalance | 1.67 % positives in training, 2.34 % in test |
| Missingness | 8.33 % of cells empty, 8 columns above 65 % |
| Asymmetric cost | False alarm 10, missed failure 500, ratio 50 to 1 |

Accuracy is not the metric. The metric is the total Scania cost. The reference to beat is the cheaper of the two constant rules, and it flips between files.

| File | Flag nothing | Flag everything | Reference |
|---|---|---|---|
| Official test, 16,000 rows | 187,500 | 156,250 | flag everything |
| Reserved, 12,000 rows | 100,000 | 118,000 | flag nothing |

## Approach

Three measurements, in the order the protocol prescribes. No later measurement informs an earlier one.

**1. Benchmark, 5 folds on 48,000 rows.** Compares the five families under one protocol.

**2. Repeated cross-validation, 6 partitions, 30 measurements.** Designates the two finalists. Paired gap 396 units, detection floor 354.

**3. Arbitration, 12,000 reserved rows, opened once.** Gradient boosting 6,410, random forest 7,310. Gap 900 under the 2,000 margin. Retained model: gradient boosting.

**Three engineering points:**

- **Missingness treated as signal.** 8 columns absent in a perfect cascade (9 patterns out of 256, no exception) summarised into one absence depth. 56 non-nested columns grouped into 9 flags by tier. Variables built before imputation, which would destroy the pattern.
- **Cost ratio enters once.** 50:1 weighting carries the cost, threshold measured by exhaustive sweep. Otherwise effective ratio of 2,501:1.
- **Threshold tuned out of sample.** Inner cross-validation inside each fold. Random forest went from 41,050 to 6,926, a factor of 5.9.

## Models used

Five families, deliberately coarse tuning and comparable effort.

| Model | Configuration |
|---|---|
| Gradient boosting | XGBoost, depth 8, rate 0.1, 300 trees |
| Random forest | scikit-learn, 300 trees, unlimited depth |
| Keras perceptron | 2 layers (64, 32), dropout 0.3, Adam 10⁻³ |
| Linear SVM | LinearSVC C=0.001, Platt calibration 3 folds |
| Logistic regression | liblinear C=0.001, 2,000 iterations |

## Results

**Benchmark, 5 folds:**

| Model | Recall | Precision | AUC-PR | AUC-ROC |
|---|---|---|---|---|
| Gradient boosting | 95.4 % | 35.3 % | 0.878 | 0.989 |
| Random forest | 96.3 % | 28.2 % | 0.830 | 0.986 |
| Perceptron (64, 32) | 94.0 % | 29.4 % | 0.760 | 0.985 |
| Linear SVM | 92.0 % | 33.9 % | 0.757 | 0.981 |
| Logistic regression | 92.8 % | 28.3 % | 0.744 | 0.977 |
| Constant control | 0.0 % | - | 0.017 | 0.500 |

**Official test, single opening:**

| | |
|---|---|
| Cost | **11,370** |
| Constant reference | 156,250 |
| Saving | **92.7 %** |
| Recall | 96.0 % (360/375) |
| Missed failures | 15 |
| False alarms | 387 |

2016 IDA podium, same test, same metric: 9,920, 10,900, **11,370**, 11,480. Third of four. At equal detection with fourth place (15 missed failures), the 110-unit gap is entirely false alarms (387 vs 398).

Figures: [reports/test_result.json](reports/test_result.json).

## Difficulties encountered

13 difficulties in weeks 1 and 2: 2 comprehension, 7 method errors, 5 technical obstacles.

**Method errors**, invisible in the produced result:

- Biased selection grid: one criterion rewarded a degraded dataset.
- Candidate eliminated at the wrong stage (Engine Health).
- Deliverable missing its first requirement (model family selection).
- Recommendation contradicting the same document's reasoning.
- Decision reversed without being named.
- Inversion copied from an official source. Rule adopted: recompute any total given with its detail.
- Wrong writing register.

**Technical obstacles**, solved the same day except one:

- Python 3.14 incompatible with TensorFlow 3.13. Python 3.13 installed alongside.
- `na` values as text, columns read as text, missingness counted as zero. Check shapes and dtypes.
- 8.3 % average missingness hiding 8 columns above 65 %. Second indicator added.
- Dataset distributed under a false name on Kaggle (ship engine, not automotive).
- Windows/Linux line endings. Rule: repository is the single reference.
- Decision threshold tuned in-sample: 82 missed failures per fold instead of 6. Defect invisible without an execution error.

Full detail: [docs/method_notes.md](docs/method_notes.md).

## Outlook

- **Histogram groups not treated.** 70 columns handled as plain counters. Deriving shape features: most direct lead.
- **Missingness variables show no measurable gain.** 6 paired comparisons, none significant. Effect below noise, or trees recovering the information on their own.
- **Signal reduces to a wear indicator.** Permutation importance: `aa_000` on top. Model preferentially misses least-used vehicles (median counter 199,744 for the 15 missed failures, against 634,684 for detected ones).
- **No temporal dimension.** Single collection campaign, no timestamped data, drift not measurable.
- **Column anonymisation.** Structural analysis, no physical recommendation such as "monitor this component".
- **Model not optimised for inference.** 277 ms on Raspberry Pi 4 against 50 ms on development machine. Conversion to an optimised inference format would ease deployment.

## Layout

```
src/          config, seeding, cost, data, missingness, preprocessing,
              evaluation, models, losses, inference
scripts/      download, check_cost_function, build_dataset, verify,
              paired_comparisons, finalists, calibration, latency
tests/        40 tests, 5 modules
notebooks/    00 selection, 01 exploration, 02 benchmark, 03 ablation,
              04 cost-sensitive losses, 05 arbitration, 06 final test
app/          Streamlit demonstrator
docs/         protocol, decisions, journal, sheets, bibliography
reports/      result tables, source of truth
data/, models/  not versioned, regenerated by script
```

**Rule**: files in `reports/` are the source of truth. No figure typed by hand.

## Installation

Python 3.13 required (TensorFlow does not support 3.14). The container image needs neither.

```bash
python3.13 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./scripts/download_data.sh
./.venv/bin/python scripts/check_cost_function.py
./.venv/bin/python scripts/build_dataset.py
./.venv/bin/python -m pytest
./.venv/bin/python scripts/verify.py
```

Demonstrator:

```bash
./scripts/fetch_models.sh
docker compose up --build   # http://localhost:8501
```

## Requirements

| ID | Requirement | State |
|---|---|---|
| EF01 | Loading and exploratory analysis | done |
| EF02 | Reproducible preparation chain | done |
| EF03 | Four classical models | done |
| EF04 | One Keras neural network | done |
| EF05 | Common protocol and Scania cost | done |
| EF06 | Comparative benchmark and justified choice | done |
| EF07 | Serialisation of the selected model | done |
| EF08 | Prediction demonstrator | done |
| EF09 | Real-time stream simulation | dropped |
| ENF01 | Python 3 and venv under Ubuntu | done |
| ENF02 | Git, code in English, documentation in French | done |
| ENF03 | Reproducibility: seeds, pinned versions | done |
| ENF04 | Runs without GPU | done |
| ENF05 | Docker image of the demonstrator | done |
| ENF06 | Single prediction under 1 s | done, 50 ms median |

## Sources

Dataset: APS Failure at Scania Trucks, Scania CV AB, 2016, UCI Machine Learning Repository, GPLv3. Dataset sheet: [docs/dataset_scania.md](docs/dataset_scania.md). Bibliography: [docs/references.bib](docs/references.bib).
