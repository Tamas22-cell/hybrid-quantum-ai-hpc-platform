"""Independent classical readout mitigation and three-qubit bit-flip code."""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix, partial_trace, state_fidelity, Statevector

def mitigate(probabilities, error):
    if not 0 <= error < .5:
        raise ValueError("Readout error must be below 0.5")
    p=np.asarray(probabilities,dtype=float)
    if p.shape != (2,) or np.any(p<0) or not np.isclose(p.sum(),1):
        raise ValueError("Invalid probabilities")
    channel=np.array([[1-error,error],[error,1-error]])
    corrected=np.maximum(np.linalg.solve(channel,p),0)
    return corrected/corrected.sum()

def bit_flip_code(error_wire=None):
    if error_wire not in (None,0,1,2):
        raise ValueError("Invalid error wire")
    c=QuantumCircuit(3)
    c.ry(.73,0)
    c.cx(0,1)
    c.cx(0,2)
    if error_wire is not None:
        c.x(error_wire)
    c.cx(0,1)
    c.cx(0,2)
    c.ccx(1,2,0)
    reference=QuantumCircuit(1)
    reference.ry(.73,0)
    decoded=partial_trace(DensityMatrix.from_instruction(c),[1,2])
    return float(state_fidelity(decoded,Statevector.from_instruction(reference)))
