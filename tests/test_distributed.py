import pytest

def test_ray_reference():
    pytest.importorskip("ray")
    from distributed_engine.core import benchmark
    result=benchmark(17,2,2)
    assert result["max_abs_error"] < 1e-9
    assert result["median_seconds"] > 0
