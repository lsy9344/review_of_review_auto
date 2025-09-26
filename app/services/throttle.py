"""Randomized delay and speed control (placeholder)."""

import random
import time


def sleep_random(min_seconds: float = 2.0, max_seconds: float = 6.0) -> None:
    time.sleep(random.uniform(min_seconds, max_seconds))
