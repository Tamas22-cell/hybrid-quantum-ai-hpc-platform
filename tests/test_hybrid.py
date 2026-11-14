import pytest

def test_vqe():
    pytest.importorskip("pennylane")
    from hybrid_engine.vqe import solve
    assert abs(solve()["gap"]) < 1e-5

def test_qaoa():
    pytest.importorskip("qiskit")
    pytest.importorskip("scipy")
    from hybrid_engine.qaoa import solve
    r = solve()
    assert sum(r["portfolio"]) == 2
    assert r["cost"] >= r["exact"] - 1e-9
    assert 0 <= r["optimal_probability"] <= 1

def test_qml():
    pytest.importorskip("pennylane")
    pytest.importorskip("torch")
    from hybrid_engine.qml_model import train
    r = train()
    assert r["final_loss"] < r["initial_loss"]
