import pytest
from gpu_engine.core import benchmark

def test_invalid_size():
    with pytest.raises(ValueError):
        benchmark(0)

def test_torch_cpu():
    pytest.importorskip("torch")
    result = benchmark(16,2,device="cpu")
    assert result["device"] == "cpu"
    assert result["max_abs_error"] < 1e-9

@pytest.mark.parametrize("backend", ["torch","cupy"])
def test_cuda(backend):
    lib = pytest.importorskip(backend)
    if backend == "torch":
        if not lib.cuda.is_available():
            pytest.skip("No CUDA device")
    else:
        try:
            count = lib.cuda.runtime.getDeviceCount()
        except lib.cuda.runtime.CUDARuntimeError:
            pytest.skip("No CUDA runtime")
        if not count:
            pytest.skip("No CUDA device")
    assert benchmark(32,2,backend=backend)["max_abs_error"] < 1e-9
