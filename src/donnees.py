"""Loading and splitting. The test file is sealed until week 8."""

from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from src.config import (CIBLE, ETIQUETTE_POSITIVE, FICHIER_TEST, FICHIER_TRAIN,
                        GRAINE, JETON_ABSENT, PART_VALIDATION)


def _ligne_entete(chemin: Path) -> int:
    """Locate the header line. UCI files carry a ~20-line GPL preamble that
    the Kaggle mirror does not, so detect it rather than hard-code skiprows.
    """
    with open(chemin, "r", encoding="utf-8", errors="ignore") as f:
        for i, ligne in enumerate(f):
            if ligne.lower().startswith(f"{CIBLE},"):
                return i
    raise ValueError(f"Aucune ligne d'en-tête trouvée dans {chemin}")


def charge(partie: str = "train") -> pd.DataFrame:
    """Load one split, with numeric features and a 0/1 target.

    Convention, never to be inverted: 1 = APS failure = rare class.
    """
    chemin = {"train": FICHIER_TRAIN, "test": FICHIER_TEST}[partie]
    if not chemin.exists():
        raise FileNotFoundError(f"{chemin} absent. Lancer scripts/download_data.sh")

    df = pd.read_csv(chemin, skiprows=_ligne_entete(chemin),
                     na_values=JETON_ABSENT, low_memory=False)

    df[CIBLE] = (df[CIBLE] == ETIQUETTE_POSITIVE).astype(int)
    mesures = [c for c in df.columns if c != CIBLE]
    df[mesures] = df[mesures].apply(pd.to_numeric, errors="coerce")
    return df


def decoupe(graine: int = GRAINE):
    """Stratified 80/20 split of the training file, BEFORE any preparation.

    Stratification is not cosmetic here: an unstratified draw can move the
    validation part across the 1.96% break-even rate, which flips which naive
    rule is cheaper on it.
    """
    df = charge("train")
    X, y = df.drop(columns=[CIBLE]), df[CIBLE]
    return train_test_split(X, y, test_size=PART_VALIDATION,
                            stratify=y, random_state=graine)


def test_scelle():
    """Load the sealed test set. Do not call before week 8."""
    df = charge("test")
    return df.drop(columns=[CIBLE]), df[CIBLE]
