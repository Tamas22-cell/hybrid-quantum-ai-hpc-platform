import argparse
import json
from quantum_engine.core import benchmark

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--backend", choices=["qiskit","cudaq"], default="qiskit")
    p.add_argument("--qubits", type=int, default=4)
    p.add_argument("--repeats", type=int, default=5)
    a = p.parse_args()
    print(json.dumps(benchmark(a.qubits,a.repeats,a.backend),indent=2))
