"""Replay the full preparation chain and check it against known figures.

Writes data/processed/. Run from the project root:
    ./.venv/bin/python scripts/build_dataset.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402

from src.config import PROCESSED_DIR  # noqa: E402
from src.cost import constant_rule_costs  # noqa: E402
from src.data import train_validation_split  # noqa: E402
from src.missingness import (MissingnessEncoder, detect_groups,  # noqa: E402
                            duplicate_absence_columns, gap_cliff,
                            nesting_report, sub_block_homogeneity)
from src.preprocessing import Preprocessor, save  # noqa: E402
from src.seeding import set_seed  # noqa: E402


def main() -> None:
    set_seed()

    X_fit, X_val, y_fit, y_val = train_validation_split()
    print(f"Fitting    : {X_fit.shape}, {int(y_fit.sum())} failures "
          f"({y_fit.mean():.4%})")
    print(f"Validation : {X_val.shape}, {int(y_val.sum())} failures "
          f"({y_val.mean():.4%})")
    assert X_fit.shape == (48000, 170) and X_val.shape == (12000, 170)
    assert int(y_fit.sum()) == 800 and int(y_val.sum()) == 200
    print(f"Split checksum : {int(X_val.index.to_numpy().sum()):,}")

    groups = detect_groups(X_fit, y_fit)
    print(f"\nGroup 1 : {len(groups['group1'])} columns -> {groups['group1']}")
    print(f"Group 2 : {len(groups['group2'])} columns")
    print(f"Mute    : {len(groups['mute'])} columns")
    assert sum(len(groups[k]) for k in ("group1", "group2", "mute")) == 170

    cliff = gap_cliff(X_fit, y_fit)
    for side in ("group1_cliff", "group2_cliff"):
        drop = cliff[side]
        if drop:
            print(f"{side:<13} : last selected {drop['last_selected']:.3f}, "
                  f"next {drop['next']:.3f}, factor {drop['factor']:.1f}")

    nested = nesting_report(X_fit, groups["group1"])
    print(f"\nGroup 1 nesting : {nested['n_patterns']} patterns, "
          f"{nested['n_if_nested']} expected if nested, "
          f"{nested['nested_share']:.2%} of rows, "
          f"{nested['n_exceptions']} exceptions")
    assert nested["n_exceptions"] == 0

    # Group 2 fails this test, which is why it is not summed into a depth.
    not_nested = nesting_report(X_fit, groups["group2"])
    print(f"Group 2 nesting : {not_nested['n_patterns']} patterns, "
          f"{not_nested['n_if_nested']} expected if nested, "
          f"{not_nested['nested_share']:.2%} of rows, "
          f"{not_nested['n_exceptions']} exceptions")
    assert not_nested["n_exceptions"] > 0

    duplicates = duplicate_absence_columns(X_fit)
    print(f"\nPerfectly correlated absence pairs : {duplicates}")

    encoder = MissingnessEncoder().fit(X_fit, y_fit)
    print(f"\nGroup 2 sub-blocks : {len(encoder.sub_blocks_)}")
    print(sub_block_homogeneity(X_fit, encoder.sub_blocks_).to_string(index=False))
    print(f"Representative columns : {encoder.representatives_}")

    X_fit_encoded = encoder.transform(X_fit)
    X_val_encoded = encoder.transform(X_val)
    print(f"\nAfter encoding : {X_fit_encoded.shape} and {X_val_encoded.shape}")

    unscaled = ["depth_g1"] + encoder.flag_names_
    preprocessor = Preprocessor(group1=encoder.group1_,
                                unscaled=unscaled).fit(X_fit_encoded)

    X_fit_final = preprocessor.transform(X_fit_encoded)
    X_val_final = preprocessor.transform(X_val_encoded)
    assert X_fit_final.isna().sum().sum() == 0
    assert X_val_final.isna().sum().sum() == 0

    load = X_fit_encoded.isna().mean()
    print("\nImputation load :")
    for level in (0.10, 0.30, 0.50, 0.65):
        print(f"  columns imputed above {level:.0%} : {int((load > level).sum())}")

    # Leakage evidence. If the fitted medians equalled the medians of the two
    # parts pooled together, the validation part would have contributed.
    pooled = pd.concat([X_fit_encoded, X_val_encoded])[preprocessor.others_]
    n_different = int((preprocessor.medians_ != pooled.median()).sum())
    print(f"\nMedians differing from the pooled median : {n_different} columns")

    scaled = preprocessor.to_scale_
    print(f"Fitting    : mean {X_fit_final[scaled].mean().mean():.2e}, "
          f"std {X_fit_final[scaled].std().mean():.4f}")
    print(f"Validation : mean {X_val_final[scaled].mean().mean():.4f}, "
          f"std {X_val_final[scaled].std().mean():.4f}")
    print("  a validation std of exactly 1.0 would indicate leakage")

    constant = [c for c in scaled if X_fit_final[c].std() == 0]
    print(f"\nConstant columns : {constant}")
    for column in constant:
        before = X_fit_encoded[column]
        print(f"  {column} : {before.nunique()} distinct value(s) before "
              f"imputation, value {before.dropna().iloc[0]:,.0f}, "
              f"{before.isna().mean():.1%} missing")

    print("\nConstant rules on validation :")
    for key, value in constant_rule_costs(y_val).items():
        print(f"  {key:<18} {value}")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    X_fit_final.to_csv(PROCESSED_DIR / "X_fit.csv", index=True)
    X_val_final.to_csv(PROCESSED_DIR / "X_val.csv", index=True)
    y_fit.to_csv(PROCESSED_DIR / "y_fit.csv", index=True)
    y_val.to_csv(PROCESSED_DIR / "y_val.csv", index=True)
    save(encoder, "missingness_encoder.joblib")
    save(preprocessor, "preprocessor.joblib")

    print(f"\nFinal shapes : {X_fit_final.shape} and {X_val_final.shape}")
    print(f"Checksum     : {X_fit_final.values.sum():,.2f}")


if __name__ == "__main__":
    main()
