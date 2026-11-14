import pytest
from quantum_engine.core import benchmark

@pytest.mark.parametrize("backend", ["qiskit", "cudaq"])
@pytest.mark.parametrize("qubits", [2, 4])
def test_ghz(backend, qubits):
    pytest.importorskip(backend)
    result = benchmark(qubits, 2, backend)
    assert result["fidelity"] == pytest.approx(1, abs=1e-6)
    assert result["norm"] == pytest.approx(1, abs=1e-6)

def test_invalid_qubits():
    with pytest.raises(ValueError):
        benchmark(1)
