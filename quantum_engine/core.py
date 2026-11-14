"""GHZ state preparation on independent quantum simulators."""
import time
import numpy as np

def benchmark(qubits=3, repeats=5, backend="qiskit"):
    if not 2 <= qubits <= 20 or not 1 <= repeats <= 100:
        raise ValueError("Invalid qubits or repeats")
    if backend == "qiskit":
        from qiskit import QuantumCircuit
        from qiskit.quantum_info import Statevector
        circuit = QuantumCircuit(qubits)
        circuit.h(0)
        for i in range(1, qubits):
            circuit.cx(0, i)
        simulate = lambda: np.asarray(Statevector.from_instruction(circuit).data)
    elif backend == "cudaq":
        import cudaq
        kernel = cudaq.make_kernel()
        q = kernel.qalloc(qubits)
        kernel.h(q[0])
        for i in range(1, qubits):
            kernel.cx(q[0], q[i])
        simulate = lambda: np.asarray(cudaq.get_state(kernel))
    else:
        raise ValueError("Unknown backend")
    simulate()
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        state = simulate()
        times.append(time.perf_counter() - start)
    expected = np.zeros(2**qubits, dtype=complex)
    expected[[0,-1]] = 1/np.sqrt(2)
    fidelity = float(abs(np.vdot(expected, state))**2)
    return dict(backend=backend, execution="simulator", qubits=qubits,
                repeats=repeats, median_seconds=float(np.median(times)),
                fidelity=fidelity, norm=float(np.linalg.norm(state)))
