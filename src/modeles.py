"""Model zoo for the benchmark.

Class weighting is 50:1, taken from the cost matrix, NOT class_weight="balanced"
which would give the 59:1 observed frequency ratio. The cost enters the chain
once and only once (D-11).
"""

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from src.config import GRAINE, PONDERATION


def regression_logistique(C: float = 0.01):
    """Interpretable floor, and the best candidate for calibration diagnosis."""
    return LogisticRegression(C=C, solver="liblinear", max_iter=2000,
                              class_weight=PONDERATION, random_state=GRAINE)


def foret_aleatoire(n_arbres: int = 300, profondeur_max=None,
                    min_feuille: int = 1):
    """Winner of the 2016 challenge. Weighting applied per bootstrap sample."""
    return RandomForestClassifier(
        n_estimators=n_arbres, max_depth=profondeur_max,
        min_samples_leaf=min_feuille, class_weight=PONDERATION,
        random_state=GRAINE, n_jobs=-1,
    )

