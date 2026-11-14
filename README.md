# Hybrid Quantum–AI HPC Engineering Platform

[![CI](https://github.com/Tamas22-cell/hybrid-quantum-ai-hpc-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/Tamas22-cell/hybrid-quantum-ai-hpc-platform/actions/workflows/ci.yml)

Research platform for CPU, GPU and quantum workload orchestration.

## V1.0 CPU baseline
NumPy and MPI matrix multiplication with seeded inputs, reference validation, median latency, estimated GFLOPS, MPI speedup and efficiency.

On Linux with Open MPI installed:
```bash
pip install -r requirements-dev.txt
python -m pytest -v
python -m cpu_engine --size 256 --repeats 5
python benchmarks/mpi_scaling.py
```

MPI timings include scatter, broadcast and gather; they exclude input generation and reference validation. Speedup compares one MPI rank with two ranks under a single-thread BLAS limit. Small workloads may slow down. CI artifacts contain measured results, not hardware-independent performance claims.

## Roadmap
V1 CPU; V2 GPU; V3 quantum; V4 hybrid algorithms; V5 distributed computing; V6 AI orchestration; V7 compiler and error correction; V8 benchmarking; V9 cloud; V10 dashboard; V11 security and monitoring; V12 validated release.

Current status: V1 CI validated; V2 CPU CI passed, GPU hardware validation pending; V3 simulator implementation submitted.

## V2.0 — GPU acceleration
PyTorch CUDA and optional CuPy float64 matrix multiplication; synchronized compute-only timings exclude host/device transfers. CPU reference validates numerical accuracy. Install requirements-gpu.txt with a CUDA-enabled PyTorch build or requirements-cupy.txt with a compatible CUDA 12 runtime. Run `python -m benchmarks.cpu_gpu --backend torch` on a GPU host. CPU CI exercises PyTorch CPU only; CUDA tests skip without hardware. No GPU speedup claimed until measured.

## V3.0 — Quantum simulation
Independent Qiskit and CUDA-Q GHZ statevector benchmarks. CUDA-Q uses the CPU simulator (`qpp-cpu`); measurements report fidelity, normalization and median execution latency. Install requirements-quantum.txt or requirements-cudaq.txt and run `python -m benchmarks.quantum --backend qiskit` (or `cudaq`). No physical QPU execution is claimed.

## V4.0 — Hybrid algorithms
PennyLane VQE compared to exact diagonalization, Qiskit QAOA on a synthetic four-asset portfolio compared to exhaustive enumeration, and PennyLane/PyTorch QML training compared to a classical cosine baseline. These are small simulator experiments, not investment advice or quantum advantage claims.

## V5.0 — Distributed computing
Ray local multi-process task scheduling complements MPI. Matrix rows are partitioned across tasks, with a shared operand in the object store. Benchmark one versus two CPU slots using `python -m benchmarks.distributed` after installing requirements-distributed.txt. Timings include dispatch and result collection, excluding startup and initial object placement. Multi-node validation remains pending.

## V6.0 — Backend orchestrator
Rule-based scheduling selects CPU, CUDA or Ray for matrix tasks and a quantum simulator for circuits. GPU/Ray capability flags are supplied by callers; runtime failures trigger ordered fallback and structured attempt records. Thresholds are initial heuristics, not learned or cost-calibrated policies. Physical QPU selection and learned scheduling remain future work.

## V7.0 — Compiler and error control
Qiskit level-3 transpilation compares circuit depth, gate count and state fidelity. A calibrated symmetric single-bit readout model demonstrates mitigation, and a three-qubit repetition circuit corrects one injected bit flip. Run `python -m benchmarks.compiler`. This is not fault-tolerant quantum computing or hardware noise validation.
