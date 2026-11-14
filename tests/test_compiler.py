import pytest
import numpy as np
pytest.importorskip("qiskit")
from quantum_engine.compiler import benchmark
from quantum_engine.error_control import mitigate, bit_flip_code

def test_compiler():
    r=benchmark()
    assert r["optimized_gates"] < r["original_gates"]
    assert r["optimized_depth"] <= r["original_depth"]
    assert r["fidelity"] == pytest.approx(1)

@pytest.mark.parametrize("wire",[None,0,1,2])
def test_error_correction(wire):
    assert bit_flip_code(wire)==pytest.approx(1)

def test_readout():
    assert np.allclose(mitigate([.9,.1],.1),[1,0])
