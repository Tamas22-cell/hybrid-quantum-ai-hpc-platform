"""Bounded Ray task pool with deterministic reference validation."""
import time
import numpy as np
import ray

@ray.remote(num_cpus=1)
def multiply(a,b):
    return a @ b

def benchmark(size=256, workers=2, repeats=3):
    if not 1 <= workers <= 8 or not 1 <= size <= 2048 or not 1 <= repeats <= 20:
        raise ValueError("Invalid workload")
    a,b = np.random.default_rng(42).standard_normal((2,size,size))
    expected = a @ b
    owned = not ray.is_initialized()
    if owned:
        ray.init(num_cpus=workers, include_dashboard=False)
    try:
        chunks = np.array_split(a, workers)
        shared = ray.put(b)
        def execute():
            return np.concatenate(ray.get([multiply.remote(x,shared) for x in chunks]))
        execute()
        times=[]
        for _ in range(repeats):
            start=time.perf_counter()
            actual=execute()
            times.append(time.perf_counter()-start)
        np.testing.assert_allclose(actual,expected,rtol=1e-9,atol=1e-9)
        return dict(workers=workers,size=size,median_seconds=float(np.median(times)),
                    max_abs_error=float(np.max(np.abs(actual-expected))))
    finally:
        if owned:
            ray.shutdown()
