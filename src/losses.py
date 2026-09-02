"""Loss functions encoding the Scania cost matrix.

The neural network is the only model in the benchmark whose objective can be
rewritten; the four classical models have theirs imposed by the method that
defines them (docs/technical_decisions.md).
"""

import tensorflow as tf

from src.config import COST_FN, COST_FP

EPSILON = 1e-7


def weighted_cross_entropy(cost_fp: float = COST_FP, cost_fn: float = COST_FN,
                           normalise: bool = True):
    """Cross-entropy weighted by the business cost of each error type.

    normalise divides by cost_fp to keep the loss at a readable magnitude. It
    is a pure rescaling and only shifts the learning-rate scale.
    """
    scale = cost_fp if normalise else 1.0

    def loss(y_true, y_predicted):
        y_true = tf.cast(y_true, tf.float32)
        y_predicted = tf.clip_by_value(y_predicted, EPSILON, 1.0 - EPSILON)

        missed = cost_fn * y_true * tf.math.log(y_predicted)
        false_alarm = cost_fp * (1.0 - y_true) * tf.math.log(1.0 - y_predicted)

        return -tf.reduce_mean(missed + false_alarm) / scale

    loss.__name__ = "weighted_cross_entropy"
    return loss


def focal_loss(alpha: float = 0.75, gamma: float = 2.0):
    """Discount well-classified examples so hard ones dominate the gradient.

    alpha balances the two classes, gamma sets how sharply the discount
    applies. gamma = 0 reduces this to a weighted cross-entropy.
    """
    def loss(y_true, y_predicted):
        y_true = tf.cast(y_true, tf.float32)
        y_predicted = tf.clip_by_value(y_predicted, EPSILON, 1.0 - EPSILON)

        p_true = y_true * y_predicted + (1.0 - y_true) * (1.0 - y_predicted)
        alpha_t = y_true * alpha + (1.0 - y_true) * (1.0 - alpha)

        return -tf.reduce_mean(alpha_t * tf.pow(1.0 - p_true, gamma)
                               * tf.math.log(p_true))

    loss.__name__ = "focal_loss"
    return loss


def weighted_focal_loss(cost_fp: float = COST_FP, cost_fn: float = COST_FN,
                        gamma: float = 2.0):
    """Both mechanisms at once: cost by class, discount by difficulty."""
    scale = cost_fp

    def loss(y_true, y_predicted):
        y_true = tf.cast(y_true, tf.float32)
        y_predicted = tf.clip_by_value(y_predicted, EPSILON, 1.0 - EPSILON)

        p_true = y_true * y_predicted + (1.0 - y_true) * (1.0 - y_predicted)
        weight = y_true * cost_fn + (1.0 - y_true) * cost_fp

        return -tf.reduce_mean(weight * tf.pow(1.0 - p_true, gamma)
                               * tf.math.log(p_true)) / scale

    loss.__name__ = "weighted_focal_loss"
    return loss
