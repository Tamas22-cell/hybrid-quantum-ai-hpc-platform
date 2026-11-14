"""Compare MPI end-to-end wall times with the same workload and BLAS thread limit."""
import json
import os
import subprocess
import sys

def main():
    env = dict(os.environ, OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1")
    results = []
    for workers in (1, 2):
        output = subprocess.check_output(["mpiexec", "-n", str(workers),
            sys.executable, "-m", "cpu_engine.mpi_engine", "--size", "512",
            "--repeats", "5"], env=env, text=True, timeout=120)
        results.append(json.loads(output))
    base = results[0]["median_seconds"]
    for result in results:
        result["speedup"] = base / result["median_seconds"]
        result["efficiency"] = result["speedup"] / result["workers"]
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
