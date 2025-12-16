from __future__ import annotations

import asyncio
import random
from typing import Iterable, Sequence


def human_delay(base: float = 0.4, variance: float = 0.4) -> float:
    """Return a small randomized delay to mimic human interaction."""

    jitter = random.random() * variance
    return max(0.05, base + jitter)


def choice_weighted(options: Sequence[str], weights: Sequence[float]) -> str:
    total = sum(weights)
    pick = random.random() * total
    acc = 0.0
    for option, weight in zip(options, weights):
        acc += weight
        if pick <= acc:
            return option
    return options[-1]


def cycle_with_bias(items: Iterable[str], shuffle: bool = True) -> Iterable[str]:
    pool = list(items)
    if shuffle:
        random.shuffle(pool)
    while True:
        for item in pool:
            yield item
        if shuffle:
            random.shuffle(pool)


async def sleep_human(min_seconds: float = 0.3, max_seconds: float = 0.9) -> None:
    await asyncio.sleep(random.uniform(min_seconds, max_seconds))
