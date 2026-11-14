"""Deterministic CPU baseline for HPC workloads."""
import time
import numpy as np

def benchmark(size: int = 256, repeats: int = 5, seed: int = 42) -> dict:
    if not 1 <= size <= 2048 or not 1 <= repeats <= 100:
        raise ValueError("Invalid size or repeat count")
    rng = np.random.default_rng(seed)
    a, b = rng.standard_normal((2, size, size))
    a @ b  # warm-up
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        c = a @ b
        times.append(time.perf_counter() - start)
    median = float(np.median(times))
    return {"backend": "cpu_numpy", "size": size, "repeats": repeats,
            "median_seconds": median, "gflops": 2 * size**3 / median / 1e9,
            "checksum": float(c.sum()), "seed": seed}
