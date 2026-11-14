import itertools
import numpy as np
from scipy.optimize import minimize
from qiskit import QuantumCircuit
from qiskit.circuit.library import DiagonalGate
from qiskit.quantum_info import Statevector

def solve():
    # Toy cardinality-constrained portfolio, two of four assets.
    returns = np.array([.09,.06,.12,.04])
    risk = np.diag([.04,.02,.09,.01])
    bits = np.array(list(itertools.product([0,1], repeat=4)))[:,::-1]
    costs = np.array([x @ risk @ x - returns @ x + (x.sum()-2)**2 for x in bits])
    def probabilities(theta):
        gamma,beta = theta
        c = QuantumCircuit(4)
        c.h(range(4))
        c.append(DiagonalGate(np.exp(-1j*gamma*costs)),range(4))
        for i in range(4):
            c.rx(2*beta,i)
        return Statevector.from_instruction(c).probabilities()
    opt = minimize(lambda t: probabilities(t) @ costs,[.5,.3],method="Nelder-Mead")
    p = probabilities(opt.x)
    feasible = np.flatnonzero(bits.sum(axis=1)==2)
    chosen = feasible[np.argmax(p[feasible])]
    exact = feasible[np.argmin(costs[feasible])]
    return {"portfolio":bits[chosen].tolist(),"cost":float(costs[chosen]),"exact":float(costs[exact]),"optimal_probability":float(p[exact]),"feasible_probability":float(p[feasible].sum())}
