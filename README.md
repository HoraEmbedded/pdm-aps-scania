# Predictive maintenance on the Scania APS dataset

Cost-sensitive failure classification on the air pressure system of Scania
trucks. Five model families compared under one evaluation protocol frozen
before the first training run, then a single opening of the official test set.

Fourth-year engineering project, 10 weeks, supervised. French version:
[README.fr.md](README.fr.md).

## Result

| | |
|---|---|
| Cost on the official test set | **11 370** |
| Constant-rule reference | 156 250 |
| Saving | **92.7 %** |
| Detection rate | 96.0 %, 360 of 375 failures |
| Missed failures | 15 |
| False alarms | 387 |

Against the 2016 IDA industrial challenge podium, on the same test set and the
same metric: 9 920, 10 900, **11 370**, 11 480. Third of four, with a
deliberately coarse parameter search and five families compared under one
protocol.

The comparison with fourth place is exact: the same 15 missed failures, 387
false alarms against 398. At equal detection, the 110-unit gap is entirely
false alarms.

The test set was opened once, on a model frozen beforehand. Every figure above
is in [reports/test_result.json](reports/test_result.json). Eleven further
published results, and the three confidence levels they have to be read at,
are in [reports/published_results.csv](reports/published_results.csv).

## The problem

Trucks in this dataset are already immobilised in a workshop. The question is
not whether a truck is broken, it is whether the failure comes from the air
pressure system (APS) or from another component. A missed APS failure means the
air circuit is never inspected and the real cause stays in place.

The dataset carries 170 anonymised sensor readings per truck, published by
Scania in 2016 for the IDA industrial challenge. Three properties drive every
design decision:

| Property | Measured value |
|---|---|
| Class imbalance | 1.67% positives in the training file, 2.34% in the test file |
| Structured missingness | 8.33% of cells empty, 8 columns above 65%, one single complete column |
| Asymmetric cost | A false alarm costs 10, a missed failure 500, a ratio of 50 to 1 |

Accuracy is not the metric. The metric is the total cost of the Scania matrix,
and the reference to beat is the cheaper of the two constant rules. Which rule
that is depends on the file, because the two cost the same at a positive rate of
1.96%:

| File | Positive rate | Flag nothing | Flag everything | Reference |
|---|---|---|---|---|
| Official test set, 16 000 rows | 2.34% | 187 500 | 156 250 | flag everything |
| Reserved split, 12 000 rows | 1.67% | 100 000 | 118 000 | flag nothing |

The cheaper rule flips between the two, so a reference figure for this dataset
means nothing without the file it was measured on.

## How the model was chosen

Three measurements, in the order the protocol prescribes. Nothing later
informed anything earlier.

**1. Benchmark, 5 folds on the 48 000 fitting rows.** One fold is about 9 600
rows and 160 failures. Full table in [reports/benchmark.csv](reports/benchmark.csv).

| Model | Cost | Std | Recall | Precision |
|---|---|---|---|---|
| Gradient boosting, depth 8 | 6 554 | 827 | 0.954 | 0.353 |
| Random forest, 300 trees | 6 926 | 804 | 0.963 | 0.282 |
| Keras perceptron (64, 32) | 8 494 | 1 780 | 0.940 | 0.294 |
| Linear SVM | 9 334 | 1 465 | 0.920 | 0.339 |
| Logistic regression | 9 596 | 1 222 | 0.928 | 0.283 |
| Constant control | 80 000 | 0 | 0 | - |

The tree family beats the linear family by 2 725 units, 6 740 against 9 465 in
family means. That is a difference of means rather than a paired comparison,
but it clears the protocol's 2 000-unit arbitration margin by enough to support
a conclusion about families rather than about five particular implementations.

The two leading models are 372 units apart, well inside the margin. Five folds
cannot separate them.

**2. Repeated cross-validation, 6 partitions, 30 measurements.** Still on the
fitting rows, so still without touching anything reserved. Paired fold by fold,
the gap is 396 units for a detection floor of 354
([reports/finalists.csv](reports/finalists.csv)).

This step designates the two finalists. It does not arbitrate between them: it
is measured on the data every modelling decision was already taken on. Five
folds could not tell them apart at all, thirty measurements can, and that is
what a repeated design buys.

**3. Arbitration on the 12 000 reserved rows, opened once.**
[reports/arbitration.csv](reports/arbitration.csv) puts the gradient boosting at
6 410 and the random forest at 7 310, at equal detection, 0.97, and 6 missed
failures each. The 900-unit gap sits under the protocol's 2 000-unit margin, so
cost does not separate them here either, and the missed-failure count is a tie.

The gradient boosting was retained on the repeated-partition evidence of step 2
and on its lower dispersion across those partitions, 1 203 against 1 307.

**Two decisions, two files, two margins**, and they are easy to conflate because
both produce a figure of the same order:

| | Designating the finalists | Arbitration |
|---|---|---|
| Data | 48 000 fitting rows | 12 000 reserved rows |
| Method | repeated CV, 30 paired measurements | single measurement |
| File | `reports/finalists.csv` | `reports/arbitration.csv` |
| Gap | 396 units | 900 units |
| Yardstick | measured paired floor of 354 | the protocol's 2 000-unit margin |
| Verdict | separable | not separable |

The 396-unit paired difference is therefore not the arbitration result, and
quoting it as the deciding criterion would credit a decision to the wrong
dataset.

Stability is a weak criterion and is reported as such: the random forest has the
lower fold-to-fold dispersion on the single partition, 804 against 827, and the
ranking inverts over the 30 measurements. The differences are of the order of
ten per cent, so which model looks steadier depends on which dispersion is read.

The same opening measures how much the selection overfitted the estimate it was
selected on. Rescaled by 1.25 for the row count, the cross-validated cost
predicts 8 343 and the reserved rows gave 6 410: a gap of −23%
([reports/overfitting.csv](reports/overfitting.csv)). The gap has the opposite
sign to overfitting, so no optimistic bias is detectable. Two effects of
opposite sign are superposed there, and the measurement cannot separate them.

## Approach

Three points are where the engineering happened.

**Missingness treated as signal.** The per-column absence rate is compared
between classes. Two groups of opposite sign come out: 8 columns absent mostly
among non-APS failures, whose absence is perfectly nested, 9 patterns out of 256
with no exception, and is summed into one ordinal depth variable; 56 columns
absent mostly among APS failures, grouped into 9 sub-blocks by absence rate,
one flag per sub-block. Group 2 gets flags rather than a depth because it fails
the nesting test group 1 passes: 115 patterns where a nested block of 56
columns would give 57, and 3 860 rows breaking the rule outright. The variables
are built before imputation, which would otherwise destroy the pattern. Group 1
is then imputed with zero rather than the median, because its columns are absent
for the least used trucks.

**The cost ratio enters the chain exactly once.** Weighting the classes at 50:1
and also applying the analytical Bayes threshold of 1.96% would apply the ratio
twice, for an effective 2 501 to 1. The weighting carries the cost, the
threshold is measured by an exhaustive sweep, and `src.cost.unweight` inverts
the weighting when the measured threshold has to be compared back to the
analytical reference.

**The threshold is tuned out of sample.** The first implementation tuned it on
the fold's own training rows, where a random forest has near-perfect
probabilities. It is now tuned by an inner cross-validation inside each fold.
The random forest went from 41 050 to 6 926, a factor of 5.9; in its worst form
the leaky threshold collapsed the model onto the flag-everything rule, 94 400
per fold at a detection rate of 1.0, which is exactly the cost of flagging all
9 440 non-APS trucks in a fold.

Reasoning behind each decision: [docs/technical_decisions.md](docs/technical_decisions.md).
Protocol frozen before training: [docs/evaluation_protocol.md](docs/evaluation_protocol.md).

## What the experiments did not show

Reported because they were run, and a null result is a result.

- **Ablation and factorial plan on the missingness variables.** Six paired
  comparisons at 30 measurements each, none clearing its detection floor
  ([reports/paired_comparisons.csv](reports/paired_comparisons.csv)). The
  differences run from 3 to 111 units for floors of 223 to 285. The feature
  engineering that is the intellectual core of this project produces no
  measurable gain. A second, independent measurement agrees: the ten built
  variables carry almost no permutation importance
  ([reports/variable_importance.csv](reports/variable_importance.csv)), while
  `aa_000` alone carries 0.057.
- **Four loss functions on the perceptron.** The spread is 8 454 to 9 124, no
  difference clears the noise, and the reference configuration was kept by
  simplicity ([reports/loss_functions.csv](reports/loss_functions.csv)). Nothing
  is claimed about their dispersions either: the variance ratio between the
  reference and the weighted focal loss is 2.77 on four degrees of freedom, for
  a probability of 0.34.

What this does *not* license: dividing the non-significant ablation figure into
the significant 2 725 to claim the preparation matters some fixed number of
times less than the model choice. One effect is measurable and the other is not.

## Calibration

Out-of-fold reliability curves for the five models, in
[reports/calibration.csv](reports/calibration.csv). Two quantities are reported,
the mean predicted probability against the actual rate of 1.667%, and the Brier
score. Neither depends on any assumption about what the class weighting did to
the probabilities.

| Model | Mean probability | Brier |
|---|---|---|
| Gradient boosting | 0.0165 | 0.0052 |
| Random forest | 0.0148 | 0.0064 |
| Linear SVM | 0.0167 | 0.0076 |
| Perceptron | 0.0596 | 0.0201 |
| Logistic regression | 0.0982 | 0.0290 |

Three models stay centred on the base rate; two overshoot it by a factor of
three to six. That is the measured reason the threshold is measured rather than
derived, and it is a stronger argument for decision D-11 than the original one:
the weighting displaces probabilities by an amount that depends on the model and
is not predictable in advance, so no single analytical threshold applies to five
models compared under one protocol.

The unweighting formula is therefore not used as a calibration diagnostic. It
assumes the weighting multiplied the odds by fifty, which holds for two of the
five, and applied to the other three it manufactures an artefact: the gradient
boosting, the best calibrated of the five by Brier score, would come out at 457
times the analytical reference.

## Repository layout

```
src/                     importable library, one level, no duplication
  config.py              paths, seed, cost matrix, protocol constants
  seeding.py             seeds Python, NumPy and TensorFlow
  cost.py                cost function, threshold sweep, unweighting
  data.py                raw loading, stratified split, sealed test access
  missingness.py         group detection, depth variable, sub-block flags
  preprocessing.py       differentiated imputation then scaling
  evaluation.py          cross-validation under the frozen protocol
  models.py              the five model factories
  losses.py              cost-sensitive Keras losses
  inference.py           the frozen model, its threshold and the chain
scripts/
  download_data.sh       fetches the dataset from its primary source
  fetch_models.sh        fetches the trained weights from the release
  check_cost_function.py seven checks on the cost function
  build_dataset.py       replays the preparation chain and asserts its figures
  paired_comparisons.py  the ablation and the factorial plan
  finalists.py           the two leading models over 6 partitions
  calibration.py         reliability curves
  latency.py             single-prediction latency
  published_results.py   the literature table, with its arithmetic check
  rebuild.py             regenerates the summary tables from the fold measurements
  verify.py              23 checks a fresh clone must pass
tests/                   40 tests over 5 modules
notebooks/
  00_dataset_selection   the three candidates, and the cost metric verified
  01_exploration         missingness as signal, the split, imputation
  02_benchmark           the five models under the frozen protocol
  03_ablation            do the missingness variables pay off
  04_cost_sensitive_losses  writing the cost into the objective
  05_arbitration         the reserved rows, and the overfitting measurement
  06_final_test          the single opening of the official test set
app/streamlit_app.py     the demonstrator
docs/                    protocol, decisions, journal, dataset sheets, bibliography
reports/                 result tables, fold-level runs, figures
data/                    raw and processed, not versioned, regenerated by script
models/                  serialised models, not versioned, fetched by script
```

Data and models are not in version control; the scripts that regenerate them
are. Figures are tracked on purpose, since they are a deliverable.

**The rule this repository follows:** the files in `reports/` are the source of
truth. No figure in any document is typed by hand. Every number a document
quotes exists in a result file, and the document names that file.

## Installation

TensorFlow does not support Python 3.14, so 3.13 is required. The container
image needs neither.

```bash
python3.13 -m venv .venv
./.venv/bin/pip install -r requirements.txt   # or requirements-lock.txt
```

`requirements.txt` lists the direct dependencies. `requirements-lock.txt` pins
every transitive version. `requirements-serve.txt` is the serving subset, with
NumPy, scikit-learn and XGBoost pinned exactly because those three touch model
serialisation.

## Running

```bash
./scripts/download_data.sh                          # fetch data/raw
./.venv/bin/python scripts/check_cost_function.py   # verify the metric first
./.venv/bin/python scripts/build_dataset.py         # write data/processed
./.venv/bin/python -m pytest                        # 40 tests
./.venv/bin/python scripts/verify.py                # 23 checks
./.venv/bin/jupyter lab                             # notebooks 00 to 06
```

`check_cost_function.py` is the entry point to run first: it reconstructs the
published score of the 2016 challenge winner from its error counts, which is
what makes the cost figures here comparable to the literature. `build_dataset.py`
asserts the shapes, the class counts, the group sizes and the absence of
leakage, and prints a checksum of the final table, 313 696. Any silent change to
the chain makes it fail.

Notebook 00 additionally reads the two rejected candidate datasets. They are not
required for anything else, and its section 2 skips itself when absent.

### The demonstrator

```bash
./scripts/fetch_models.sh
docker compose up --build          # then http://localhost:8501
```

The compose file publishes the container's 8501 on the host's 8501. A plain
`docker run -p 8501:8501` serves it on 8501 instead.

Weights are not versioned in Git. They are copied into the image and published
in a GitHub release, per the compromise recorded in [docs/amendment.md](docs/amendment.md).

## Requirements coverage

The specification is the project's contractual document.

| ID | Requirement | State |
|---|---|---|
| EF01 | Loading and exploratory analysis | done, notebooks 00 and 01 |
| EF02 | Reproducible preparation chain | done, `scripts/build_dataset.py` |
| EF03 | Four classical models | done, notebook 02 |
| EF04 | One Keras neural network | done, notebooks 02 and 04 |
| EF05 | Common protocol and Scania cost | done, `src/evaluation.py` |
| EF06 | Comparative benchmark and justified choice | done, gradient boosting, separated over 30 measurements |
| EF07 | Serialisation of the selected model | done, `models/final_model.json` and `src/inference.py` |
| EF08 | Prediction demonstrator | done, `app/streamlit_app.py` |
| EF09 | Real-time stream simulation | dropped, first on the abandonment order, classed Optional |
| ENF01 | Python 3 and venv under Ubuntu | done |
| ENF02 | Git, code in English, documentation in French | done |
| ENF03 | Reproducibility: seeds, pinned versions, notebooks | done, plus `scripts/verify.py` |
| ENF04 | Runs without a GPU | done, `tensorflow-cpu` |
| ENF05 | Docker image of the demonstrator | done, reinstated by [docs/amendment.md](docs/amendment.md) |
| ENF06 | Single prediction under 1 s | done, 50 ms median and 184 ms worst over 200 calls, [reports/latency_single.csv](reports/latency_single.csv) |

## Known limits

- **The 7 histogram variable groups are not treated.** 70 columns, identified
  in [reports/dataset_report.txt](reports/dataset_report.txt), handled as
  ordinary counters. They are also the least affected by missingness, 1.13%
  against 13.38% for the isolated counters, so the missingness work never
  reached them. Deriving shape features from them is the first improvement lead.
- **The missingness variables produce no measurable gain.** Six paired
  comparisons, none significant, and near-zero permutation importance. Either
  the effect is smaller than the noise at this sample size, or the tree models
  recover the information on their own. Testing the second explanation would
  mean rerunning the plan on the logistic regression, which cannot.
- **Only one hyperparameter grid was recorded.** The logistic-regression grid
  survives with its four intermediate results; for the four other models only
  the retained configuration is known
  ([docs/hyperparameter_grids.md](docs/hyperparameter_grids.md)). No script
  replays either.
- **The frozen threshold is not the cheapest one on the test set.** 11 370
  against 10 060 at the threshold that hindsight prefers. The frozen one is the
  result; the other is a diagnostic, recorded in the same file.
- **Column names carry two anomalies**, `am_0` and `ec_00`, against three
  digits everywhere else. Carried as they are, since renaming them would break
  the correspondence with the published dataset.
- **Seeds are fixed, which makes results reproducible, not robust.** The
  repeated cross-validation over 6 partitions is what supports the
  significance claims.

## Skills this project exercised

Cost-sensitive learning and threshold optimisation under an asymmetric loss;
handling a rare class without resampling; missing-value analysis as a source of
features; leakage-free protocol design, frozen before measurement, with a
single opening of the held-out data; paired statistical comparison with an
arbitration margin declared in advance, and the separation of designating
finalists from arbitrating between them on different data; calibration
assessment on quantities free of modelling assumptions; scikit-learn and TensorFlow with a
custom estimator and custom losses; serialisation and serving behind a stable
interface; multi-stage container image; reproducible Python project
organisation with an executable verification of that reproducibility.

## Sources

Dataset: APS Failure at Scania Trucks, Scania CV AB, 2016, UCI Machine Learning
Repository, GPLv3. Dataset sheet: [docs/dataset_scania.md](docs/dataset_scania.md).
Bibliography: [docs/references.bib](docs/references.bib), selection method in
[docs/bibliography_protocol.md](docs/bibliography_protocol.md), published
results with their arithmetic check in
[reports/published_results.csv](reports/published_results.csv).
