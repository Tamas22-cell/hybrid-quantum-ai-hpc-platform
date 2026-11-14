"""Optional GPU backends with synchronized, compute-only timings."""
import time
import numpy as np

def benchmark(size=256, repeats=5, seed=42, backend="torch", device="cuda"):
    if not 1 <= size <= 2048 or not 1 <= repeats <= 100:
        raise ValueError("Invalid size or repeats")
    a, b = np.random.default_rng(seed).standard_normal((2, size, size))
    expected = a @ b
    if backend == "torch":
        import torch
        if device == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("CUDA unavailable")
        x, y = [torch.as_tensor(v, device=device) for v in (a,b)]
        sync = torch.cuda.synchronize if device == "cuda" else lambda: None
        convert = lambda v: v.cpu().numpy()
        hardware = torch.cuda.get_device_name() if device == "cuda" else "CPU"
    elif backend == "cupy" and device == "cuda":
        import cupy as cp
        x, y = cp.asarray(a), cp.asarray(b)
        sync = cp.cuda.Stream.null.synchronize
        convert = cp.asnumpy
        hardware = cp.cuda.runtime.getDeviceProperties(cp.cuda.Device().id)["name"].decode()
    else:
        raise ValueError("Unsupported backend/device")
    x @ y
    sync()
    times = []
    for _ in range(repeats):
        sync()
        start = time.perf_counter()
        c = x @ y
        sync()
        times.append(time.perf_counter() - start)
    actual = convert(c)
    np.testing.assert_allclose(actual, expected, rtol=1e-9, atol=1e-9)
    median = float(np.median(times))
    return dict(backend=backend, device=device, hardware=hardware, size=size,
                repeats=repeats, seed=seed, dtype="float64", median_seconds=median,
                gflops=2*size**3/median/1e9,
                max_abs_error=float(np.max(np.abs(actual-expected))))
