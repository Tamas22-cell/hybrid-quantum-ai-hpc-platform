import json
import os
import subprocess
import sys
import pytest

@pytest.mark.skipif(
    sys.platform == "win32" and os.environ.get("HPC_RUN_MPI") != "1",
    reason="Windows MPI integration is opt-in (HPC_RUN_MPI=1)",
)
@pytest.mark.parametrize("workers", [1, 2])
def test_mpi_reference(workers):
    env = dict(os.environ, OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1")
    out = subprocess.check_output(["mpiexec", "-n", str(workers), sys.executable,
        "-m", "cpu_engine.mpi_engine", "--size", "17", "--repeats", "2"],
        env=env, text=True, timeout=60)
    result = json.loads(out)
    assert result["workers"] == workers
    assert result["max_abs_error"] < 1e-9
    assert result["median_seconds"] > 0
