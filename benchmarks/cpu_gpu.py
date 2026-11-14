import argparse
import json
from cpu_engine.core import benchmark as cpu
from gpu_engine.core import benchmark as gpu

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--size", type=int, default=1024)
    p.add_argument("--repeats", type=int, default=5)
    p.add_argument("--backend", choices=["torch","cupy"], default="torch")
    a = p.parse_args()
    baseline = cpu(a.size,a.repeats)
    accelerated = gpu(a.size,a.repeats,backend=a.backend)
    print(json.dumps({"cpu":baseline,"gpu":accelerated,
          "compute_speedup":baseline["median_seconds"]/accelerated["median_seconds"]},indent=2))

if __name__ == "__main__":
    main()
