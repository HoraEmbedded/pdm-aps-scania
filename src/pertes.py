"""Custom loss functions encoding the Scania cost matrix.

The freedom to write the objective is the only advantage the neural network
holds over the four classical models, whose loss is imposed by the method that
defines them. This module is where that advantage is exercised.
"""

import tensorflow as tf

from src.config import COUT_FN, COUT_FP

EPSILON = 1e-7


def entropie_croisee_ponderee(cout_fp: float = COUT_FP,
                              cout_fn: float = COUT_FN,
                              normalise: bool = True):
    """Cross-entropy weighted by the business cost of each error type.

    A missed failure contributes cost_fn times the log loss, a false alarm
    cost_fp times. The gradient of a missed failure is therefore fifty times
    larger, which is exactly what the evaluation metric rewards.

    normalise divides by cost_fp so the loss keeps a readable magnitude. It is
    a pure rescaling: it moves nothing but the learning-rate scale.
    """
    echelle = cout_fp if normalise else 1.0

    def perte(y_vrai, y_predit):
        y_vrai = tf.cast(y_vrai, tf.float32)
        y_predit = tf.clip_by_value(y_predit, EPSILON, 1.0 - EPSILON)

        terme_panne_ratee = cout_fn * y_vrai * tf.math.log(y_predit)
        terme_fausse_alerte = cout_fp * (1.0 - y_vrai) * tf.math.log(1.0 - y_predit)

        return -tf.reduce_mean(terme_panne_ratee + terme_fausse_alerte) / echelle

    perte.__name__ = "entropie_croisee_ponderee"
    return perte


def perte_focale(alpha: float = 0.75, gamma: float = 2.0):
    """Focal loss: discount well-classified examples so hard ones dominate.

    alpha balances the two classes, gamma controls how sharply the discount
    applies. gamma equal to zero reduces this to a weighted cross-entropy.
    """
    def perte(y_vrai, y_predit):
        y_vrai = tf.cast(y_vrai, tf.float32)
        y_predit = tf.clip_by_value(y_predit, EPSILON, 1.0 - EPSILON)

        # Probability assigned to the true class of each observation
        p_vraie = y_vrai * y_predit + (1.0 - y_vrai) * (1.0 - y_predit)
        alpha_t = y_vrai * alpha + (1.0 - y_vrai) * (1.0 - alpha)
        attenuation = tf.pow(1.0 - p_vraie, gamma)

        return -tf.reduce_mean(alpha_t * attenuation * tf.math.log(p_vraie))

    perte.__name__ = "perte_focale"
    return perte


def focale_ponderee(cout_fp: float = COUT_FP, cout_fn: float = COUT_FN,
                    gamma: float = 2.0):
    """Both mechanisms at once: cost by class, discount by difficulty."""
    echelle = cout_fp

    def perte(y_vrai, y_predit):
        y_vrai = tf.cast(y_vrai, tf.float32)
        y_predit = tf.clip_by_value(y_predit, EPSILON, 1.0 - EPSILON)

        p_vraie = y_vrai * y_predit + (1.0 - y_vrai) * (1.0 - y_predit)
        poids = y_vrai * cout_fn + (1.0 - y_vrai) * cout_fp
        attenuation = tf.pow(1.0 - p_vraie, gamma)

        return -tf.reduce_mean(poids * attenuation * tf.math.log(p_vraie)) / echelle

    perte.__name__ = "focale_ponderee"
    return perte
