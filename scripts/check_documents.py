"""Fail if any document quotes a figure the results files do not produce.

Six inconsistencies in this project came from documents written against
prepared data that no longer existed. A search for known stale values catches
that class of error before it reaches the report. Exits non-zero, so it can be
automated.

Two kinds of entry. A stale figure is a value that was once correct and is no
longer. A forbidden phrase is a statement the measurements contradict, which is
worse, because a wrong number is a typo and a wrong statement is a claim.

Run: ./.venv/bin/python scripts/check_documents.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SEARCHED = ["docs", "README.md", "README.fr.md", "models/final_model.json"]

STALE = {
    "6 576": "6 554, gradient boosting",
    "6 714": "6 926, random forest",
    "8 550": "8 494, perceptron",
    "9 326": "9 334, linear SVM",
    "9 598": "9 596, logistic regression",
    "313 695": "313 696, checksum",
    "2 817": "2 725, gap between families",
    "6 645": "6 740, mean of the tree family",
    "9 462": "9 465, mean of the linear family",
    "119 motifs": "115 patterns, group 2 nesting",
    "4 799": "3 860 exceptions, group 2 nesting",
    "8 368": "8 454, cheapest loss variant",
    "9 210": "9 124, dearest loss variant",
    "0,325": "0,323, the group 1 cliff",
    "facteur 6,1": "facteur 5,9, effet du seuil hors echantillon",
    "93 colonnes": "85 colonnes, medianes divergentes",
    "Six verifications": "sept verifications",
    "Six vérifications": "sept vérifications",
    "six checks": "seven checks",
}

FORBIDDEN = {
    "ratio_to_bayes":
        "unweighting assumes the weighting moved the odds by fifty, true for "
        "two models of five. Report mean_probability and brier instead.",
    "facteur 457":
        "same reason: an artefact of unweighting a model it does not apply to.",
    "factor of 457":
        "same reason: an artefact of unweighting a model it does not apply to.",
    "n'a jamais été ouvert":
        "the test set was opened once, see reports/test_result.json.",
    "never been opened":
        "the test set was opened once, see reports/test_result.json.",
    "Aucun modèle sérialisé":
        "models/final_model.json and src/inference.py exist.",
    "No serialised model":
        "models/final_model.json and src/inference.py exist.",
    "treize fois moins":
        "a non-significant effect cannot be put in ratio with a significant one.",
    "thirteen times less":
        "a non-significant effect cannot be put in ratio with a significant one.",
    # The paired difference designated the finalists on the fitting rows. The
    # arbitration happened on the reserved rows and did not separate them.
    # Quoting 396 as the deciding criterion credits the wrong dataset.
    "stability across partitions":
        "state which dispersion, and that criterion 1 did not separate: see "
        "the two-decision table in the README.",
    "compteur d'usage seul":
        "the factorial plan crosses depth and the sub-block flags. aa_000 is "
        "present in all four conditions.",
    "V1_no_flags":
        "rename to V1_no_flags: the condition drops the nine flags, not aa_000.",
}


def main() -> None:
    stale_hits, forbidden_hits = [], []

    for target in SEARCHED:
        path = ROOT / target
        if not path.exists():
            continue
        files = sorted(path.rglob("*.md")) if path.is_dir() else [path]
        for file in files:
            text = file.read_text(encoding="utf-8")
            for number, line in enumerate(text.splitlines(), start=1):
                where = f"{file.relative_to(ROOT)}:{number}"
                for value, replacement in STALE.items():
                    if value in line:
                        stale_hits.append(f"{where} carries '{value}', "
                                          f"expected {replacement}")
                for phrase, reason in FORBIDDEN.items():
                    if phrase in line:
                        forbidden_hits.append(f"{where} says '{phrase}'\n"
                                              f"    {reason}")

    if stale_hits:
        print(f"{len(stale_hits)} stale figures\n")
        print("\n".join(stale_hits))
        print()
    if forbidden_hits:
        print(f"{len(forbidden_hits)} contradicted statements\n")
        print("\n".join(forbidden_hits))
        print()

    if stale_hits or forbidden_hits:
        sys.exit(1)

    print(f"no stale figure and no contradicted statement in "
          f"{', '.join(SEARCHED)}")


if __name__ == "__main__":
    main()
