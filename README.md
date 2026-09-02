# Predictive maintenance on the Scania APS dataset

Cost-sensitive failure classification on the air pressure system of Scania
trucks, with five model families compared under one frozen evaluation
protocol.

Fourth-year engineering project, 10 weeks, supervised. French version:
[README.fr.md](README.fr.md).

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
| Validation split, 12 000 rows | 1.67% | 100 000 | 118 000 | flag nothing |

The cheaper rule flips between the two, so a reference figure for this dataset
means nothing without the file it was measured on.

## Results

Mean over 5 folds of a stratified cross-validation on 48 000 rows, one fold
being roughly 9 600 rows and 160 failures. Full table in
[reports/benchmark.csv](reports/benchmark.csv).

| Model | Cost | Std | Recall | Precision |
|---|---|---|---|---|
| Gradient boosting, depth 8 | 6 576 | 1 030 | 0.955 | 0.342 |
| Random forest, 300 trees | 6 714 | 530 | 0.964 | 0.290 |
| Keras perceptron (64, 32) | 8 550 | 1 838 | 0.939 | 0.294 |
| Linear SVM | 9 326 | 1 473 | 0.920 | 0.340 |
| Logistic regression | 9 598 | 1 218 | 0.928 | 0.283 |
| Constant control | 80 000 | 0 | 0 | - |

The protocol sets the arbitration margin at 2 000 units before any measurement
is taken. The two leading models are 138 units apart for standard deviations of
530 and 1 030, so they are not separable and no winner is declared between
them.

The two families are separable: 6 645 on average for the tree ensembles against
9 462 for the linear models, a gap of 2 817 units. That is a difference of
family means rather than a paired comparison, but it clears the margin by a wide
enough factor to support a conclusion about families rather than about the five
particular implementations tested.

Two experiments were run on top of the benchmark, both reported in
[reports/](reports/):

- **Ablation and factorial plan on the missingness variables.** Six paired
  comparisons, all non-significant. The feature engineering that is the
  intellectual core of this project produces no measurable gain, which is a
  result and is reported as such. Note what this does *not* license: the
  non-significant 220 units cannot be divided into the significant 2 817 to
  claim the preparation matters some fixed number of times less than the model
  choice. One effect is measurable and the other is not
  ([docs/technical_decisions.md](docs/technical_decisions.md)).
- **Four loss functions on the perceptron.** The spread is 8 368 to 9 210, the
  differences do not clear the noise, and the reference configuration was kept
  by simplicity.

The official test set has never been opened. No test-set figure appears
anywhere in this repository.

## Approach

Three points are where the engineering actually happened.

**Missingness treated as signal.** The per-column absence rate is compared
between classes. Two groups of opposite sign come out: 8 columns absent mostly
among non-APS failures, whose absence is perfectly nested and is summed into
one ordinal depth variable; 56 columns absent mostly among APS failures,
grouped into 9 sub-blocks by absence rate, one flag per sub-block. Group 2 gets
flags rather than a depth because it fails the nesting test group 1 passes: 119
patterns where a nested block of 56 columns would give 57. The variables are
built before imputation, which would otherwise destroy the pattern. Group 1 is
then imputed with zero rather than the median, because its columns are absent
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
The random forest went from 41 050 to 6 714, a factor of 6.1; in its worst form
the leaky threshold collapsed the model onto the flag-everything rule, 94 400
per fold, at a detection rate of 1.0.

Reasoning behind each decision: [docs/technical_decisions.md](docs/technical_decisions.md).
Protocol frozen before training: [docs/evaluation_protocol.md](docs/evaluation_protocol.md).

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
scripts/                 command-line entry points
  download_data.sh       fetches the dataset from its primary source
  check_cost_function.py six checks on the cost function
  build_dataset.py       replays the preparation chain and asserts known figures
notebooks/
  00_dataset_selection   the three candidates, and the cost metric verified
  01_exploration         missingness as signal, the split, imputation
  02_benchmark           the five models under the frozen protocol
  03_ablation            do the missingness variables pay off
  04_cost_sensitive_losses  writing the cost into the objective
docs/                    protocol, decisions, journal, dataset sheets, bibliography
reports/                 result tables and figures
data/                    raw and processed, not versioned, regenerated by script
models/                  serialised models, not versioned
```

Data and models are not in version control; the scripts that regenerate them
are. Figures are tracked on purpose, since they are a deliverable.

## Installation

TensorFlow does not support Python 3.14, so 3.13 is required.

```bash
python3.13 -m venv .venv
./.venv/bin/pip install -r requirements.txt   # or requirements-lock.txt
```

`requirements.txt` lists the direct dependencies. `requirements-lock.txt` pins
every transitive version, so two installations six months apart produce the
same numbers.

## Running

```bash
./scripts/download_data.sh                          # fetch data/raw
./.venv/bin/python scripts/check_cost_function.py   # verify the metric first
./.venv/bin/python scripts/build_dataset.py         # write data/processed
./.venv/bin/jupyter lab                             # notebooks 00 to 04
```

`check_cost_function.py` is the entry point to run first: it reconstructs the
published score of the 2016 challenge winner from its error counts, which is
what makes the cost figures in this repository comparable to the literature. It
also checks the constant-rule inversion described above.

Notebook 00 additionally reads the two rejected candidate datasets. They are not
required for anything else, and its section 2 skips itself when they are absent.

`build_dataset.py` asserts the shapes, the class counts, the group sizes and
the absence of leakage, and prints a checksum of the final table. Any silent
change to the chain makes it fail.

## Requirements coverage

The specification is the project's contractual document. Coverage as of the
last commit:


## Remaining work

The project is in progress. This list is the project plan's, in its order.

1. Arbitrate between the two finalists by opening the 12 000 reserved rows once,
   which also measures how far the selection overfitted the cross-validated
   estimate it was selected on.
2. Calibration curves on the five models, then freeze the final model.
3. Open the official test set once, compare against the published figures, and
   run the error analysis and feature-importance study.
4. Prediction demonstrator (EF08) and single-prediction latency.
5. Container image, install notes, and a reproducibility check run by a
   third party.
6. Final report and defence material.

## Known limits

- **The 7 histogram variables are not treated.** The dataset contains 7 groups
  of histogram columns, 70 columns in total, identified in
  [reports/dataset_report.txt](reports/dataset_report.txt). The current chain
  treats them as ordinary counters. Deriving shape features from them is the
  first improvement lead.
- **The missingness variables produce no measurable gain.** Six paired
  comparisons, none significant. Either the effect is smaller than the noise at
  this sample size, or the tree models already recover the information on their
  own.
- **Only one hyperparameter grid was recorded.** The logistic-regression grid
  survives with its four intermediate results; for the four other models only
  the retained configuration is known. Both are documented in
  [docs/hyperparameter_grids.md](docs/hyperparameter_grids.md), and no script
  replays either.
- **No serialised model and no demonstrator.** 
- **Seeds are fixed, which makes results reproducible, not robust.** The
  repeated cross-validation over 6 partitions is what supports the
  significance claims.

## Skills this project exercised

Cost-sensitive learning and threshold optimisation under an asymmetric loss;
handling a rare class without resampling; missing-value analysis as a source of
features; leakage-free experimental protocol design, frozen before measurement;
paired statistical comparison with an arbitration margin declared in advance;
scikit-learn and TensorFlow, including a custom estimator and custom losses;
reproducible Python project organisation.

## Sources

Dataset: APS Failure at Scania Trucks, Scania CV AB, 2016, UCI Machine Learning
Repository, GPLv3. Dataset sheet: [docs/dataset_scania.md](docs/dataset_scania.md).
Bibliography: [docs/references.bib](docs/references.bib), selection method in
[docs/bibliography_protocol.md](docs/bibliography_protocol.md).
