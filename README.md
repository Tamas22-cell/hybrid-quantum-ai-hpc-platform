# Hybrid Quantum–AI HPC Engineering Platform

[![OPEN LIVE HPC PLATFORM](https://img.shields.io/badge/OPEN_LIVE_HPC_PLATFORM-2563eb?style=for-the-badge&logo=vercel&logoColor=white)](https://hybrid-quantum-ai-hpc-platform-tamas-quantum-lab.vercel.app) [![VIEW RESEARCH RELEASE](https://img.shields.io/badge/VIEW_RESEARCH_RELEASE-24292f?style=for-the-badge&logo=github)](https://github.com/Tamas22-cell/hybrid-quantum-ai-hpc-platform/releases/tag/v12.0.0-rc.1)

**Live dashboard:** operator login required. Public source code and benchmark evidence are available below.

![Hybrid Quantum–AI HPC Platform concept](9b250591-06bd-4e27-b5af-feed80ea8597.png)

*Concept visualization — illustrative metrics, not measured benchmark results.*

[![CI](https://github.com/Tamas22-cell/hybrid-quantum-ai-hpc-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/Tamas22-cell/hybrid-quantum-ai-hpc-platform/actions/workflows/ci.yml)

Research platform for CPU, GPU and quantum workload orchestration.

## Live platform

[Open the deployed HPC dashboard](https://hybrid-quantum-ai-hpc-platform.vercel.app) · [Research release](https://github.com/Tamas22-cell/hybrid-quantum-ai-hpc-platform/releases/tag/v12.0.0-rc.1)

The dashboard requires operator authentication. The public repository contains the implementation and reproducible benchmarks.

### Cloud validation — November 15, 2026

- CPU NumPy, 256 × 256 matrix: 0.735 ms median compute latency, 45.634 GFLOPS.
- Qiskit GHZ simulator, 4 qubits: 0.241 ms median compute latency, fidelity approximately 1.
- Dashboard submission, polling, persisted history, performance comparison and both export download dialogs verified in the live browser.
- Docker API integration, security checks and four export serialization tests passed in CI.

These are individual cloud benchmark results, not a CPU-versus-quantum speedup comparison. Physical QPU, cloud GPU and multi-node execution remain unvalidated. Exported local file contents were not independently inspected.

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

Current status: V12 cloud research release candidate. CPU and Qiskit workloads have persisted cloud results; physical QPU, cloud GPU and multi-node validation remain open.

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

## V8.0 — Benchmark reporting
Run `python -m benchmarks.suite` for repeated CPU and Qiskit measurements, or add `--gpu` on a CUDA host. Reports include JSON/CSV, environment metadata, median latency, p95 of run medians, reciprocal compute latency and optional cost estimated from a user-supplied hourly rate. GPU speedup compares identical matrix workloads only. MPI and Ray scaling remain separate benchmarks. Costs exclude idle time, billing granularity and transfer overhead; p95 is not a confidence interval.

## V9.0 — Cloud infrastructure
Local development: set HPC_API_KEY and POSTGRES_PASSWORD to strong URL-safe secrets and run `docker compose up --build`. The API binds to localhost:8000; `/docs` exposes OpenAPI. Submit a matrix or quantum job to `/jobs`, then poll `/jobs/{id}`. RQ processes jobs through Redis and stores successful results in PostgreSQL. The container supports CPU and Qiskit simulation. Kubernetes API deployment requires a prebuilt image, external Redis and a configured secret; worker deployment and live cluster validation are pending. Keep the development API private.

## V10.0 — Control center
Next.js dashboard in `frontend/`. Run `npm install` and `npm run dev` there with `HPC_API_URL=http://localhost:8000` set in the server environment. Vercel root directory is `frontend`; configure HPC_API_URL to an accessible secured backend before deployment. The dashboard supports CPU and quantum simulator submissions, polling and measured metrics. GPU and physical QPU execution are not exposed by the current backend. Remote deployment requires HTTPS and dashboard authentication.

## V11.0 — Security and monitoring
Configure HPC_API_KEY on the backend and server-side frontend. Job routes require X-API-Key; submissions are globally limited to ten per minute using Redis. Prometheus metrics are exposed at /metrics; sample scrape configuration and Grafana dashboard are under monitoring/. Keep metrics private. Security CI runs Bandit, pip-audit and npm audit. Shared service credentials are not individual user authentication: V12 adds single-operator dashboard access; multi-user isolation remains pending. Never publish secrets.

## V12.0 — Research release candidate
See [research protocol and validation gates](docs/RESEARCH_RELEASE.md) and [security guidance](SECURITY.md). Set HPC_UI_USER and HPC_UI_PASSWORD on the Next.js server alongside HPC_API_KEY and HPC_API_URL. Dashboard and proxy routes fail closed without credentials. Use HTTPS remotely. Cloud deployment uses Vercel, Render API and RQ worker, Redis and Neon PostgreSQL. Local CUDA measurements are separate from cloud results. Physical QPU and multi-user isolation are not validated. Release tag requires green CI on the final commit.

## Cloud architecture and validation

Authenticated browser → Next.js server proxy → FastAPI → Redis/RQ → worker → PostgreSQL. The dashboard reads the latest 100 stored results via the API and exports CSV/JSON. Historical timestamps are unknown for pre-migration records. System status checks API, Redis, PostgreSQL and worker registration; registration alone does not prove execution health. Performance summaries group measured workloads by backend and size. Validate CPU and quantum submission, polling, persisted history, export and authentication before promoting a release. Cloud GPU/QPU and Ray multi-node execution remain optional research extensions.
