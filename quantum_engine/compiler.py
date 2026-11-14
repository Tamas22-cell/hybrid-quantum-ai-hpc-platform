from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector, state_fidelity

def benchmark():
    circuit = QuantumCircuit(3)
    circuit.h(0)
    circuit.cx(0,1)
    circuit.cx(0,1)
    circuit.cx(0,1)
    circuit.cx(0,2)
    optimized = transpile(circuit, basis_gates=["h","cx","rz","sx","x"], optimization_level=3, seed_transpiler=42)
    return {"original_depth":circuit.depth(),"optimized_depth":optimized.depth(),
            "original_gates":circuit.size(),"optimized_gates":optimized.size(),
            "fidelity":float(state_fidelity(Statevector.from_instruction(circuit),Statevector.from_instruction(optimized)))}
