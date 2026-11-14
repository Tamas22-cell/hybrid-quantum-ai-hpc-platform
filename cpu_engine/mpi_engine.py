"""MPI row-distributed matrix multiplication, including communication in timing."""
import argparse
import json
import numpy as np
from mpi4py import MPI

def run(size=256, repeats=5, seed=42, comm=MPI.COMM_WORLD):
    if not 1 <= size <= 2048 or not 1 <= repeats <= 100:
        raise ValueError("Invalid size or repeats")
    rank, workers = comm.rank, comm.size
    if rank == 0:
        a, b = np.random.default_rng(seed).standard_normal((2, size, size))
        chunks = np.array_split(a, workers)
        expected = a @ b
    else:
        b = chunks = expected = None
    times = []
    for i in range(repeats + 1):
        comm.Barrier()
        start = MPI.Wtime()
        local = comm.scatter(chunks, root=0)
        shared = comm.bcast(b, root=0)
        gathered = comm.gather(local @ shared, root=0)
        elapsed = comm.reduce(MPI.Wtime() - start, op=MPI.MAX, root=0)
        if rank == 0 and i:
            times.append(elapsed)
    if rank == 0:
        actual = np.concatenate(gathered, axis=0)
        np.testing.assert_allclose(actual, expected, rtol=1e-9, atol=1e-9)
        median = float(np.median(times))
        return {"backend": "mpi_cpu", "workers": workers, "size": size,
                "repeats": repeats, "seed": seed, "median_seconds": median,
                "gflops": 2 * size**3 / median / 1e9,
                "max_abs_error": float(np.max(np.abs(actual - expected)))}
    return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, default=256)
    parser.add_argument("--repeats", type=int, default=5)
    args = parser.parse_args()
    result = run(args.size, args.repeats)
    if result is not None:
        print(json.dumps(result))
