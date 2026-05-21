"""Centralised seeded random number generator.

Every module that needs randomness must obtain an RNG through this module.
Direct use of the `random` stdlib module or `numpy.random` global state
is prohibited — this ensures reproducibility across all simulations.

Usage:
    from tarot_engine.utils.random import make_rng

    rng = make_rng(seed=42)
    rng.shuffle(deck_list)
"""

from __future__ import annotations

import random


def make_rng(seed: int) -> random.Random:
    """Create and return a seeded Random instance.

    Args:
        seed: An integer seed for reproducibility. The same seed always
              produces the same sequence of random numbers.

    Returns:
        A `random.Random` instance seeded with the given value.
    """
    return random.Random(seed)
