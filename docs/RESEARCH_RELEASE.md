# Research release candidate v1.0.0-rc.1

## Reproduction
Use Linux, Python 3.12, Open MPI and Node 22. Follow README dependency groups. Run the CI workflow and download benchmark-report, mpi-benchmark and ray-benchmark artifacts for the exact commit. Record CPU model, RAM, OS, accelerator model and driver, package versions and repetitions with each experiment.

## Validation matrix
- CPU/MPI, Ray local slots, Qiskit and CUDA-Q CPU simulation: CI.
- GPU CUDA/CuPy, multi-node deployment, physical QPU: not validated.
- VQE/QAOA/QML: small synthetic simulator experiments with classical reference.
- Scheduling: rule-based, not a trained agent.
- API: local Docker integration, not production load validation.
- Security: scoped dependency and code scans, not a penetration test.

## Experimental protocol
Use identical seeded workloads and precision for CPU/GPU. Warm up accelerators, synchronize timing, report transfer-inclusive and compute-only times separately. Repeat independent trials and report dispersion; do not infer quantum advantage from simulator timings. Use exact classical reference for small quantum problems. Archive raw samples and environment metadata. Report failures and skipped tests.

## Release gates
Green CI and security for the release commit; reproducible artifacts; documented limitations. Production rollout separately requires authenticated access, HTTPS, secrets, observability, quotas, backups and live smoke tests.
