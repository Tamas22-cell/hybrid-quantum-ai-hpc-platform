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

Current status: V1 implementation submitted; CI validation required before V2.

## V2.0 — GPU acceleration
PyTorch CUDA and optional CuPy float64 matrix multiplication; synchronized compute-only timings exclude host/device transfers. CPU reference validates numerical accuracy. Install requirements-gpu.txt with a CUDA-enabled PyTorch build or requirements-cupy.txt with a compatible CUDA 12 runtime. Run `python -m benchmarks.cpu_gpu --backend torch` on a GPU host. CPU CI exercises PyTorch CPU only; CUDA tests skip without hardware. No GPU speedup claimed until measured.
