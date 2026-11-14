import pytest
from scheduler.policy import candidates
from ai_agents.orchestrator import execute

def test_policy():
    assert candidates("matrix",1024,True,True)==["gpu","ray","cpu"]
    assert candidates("quantum",4)==["quantum_simulator"]
    with pytest.raises(ValueError):
        candidates("quantum",21)

def test_fallback():
    def fail(n):
        raise RuntimeError("GPU unavailable")
    result=execute("matrix",1024,True,handlers={"gpu":fail,"cpu":lambda n:{"size":n}})
    assert result["selected"]=="cpu"
    assert len(result["attempts"])==2

def test_cpu():
    assert execute("matrix",16)["selected"]=="cpu"
