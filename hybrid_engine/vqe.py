import numpy as np
import pennylane as qml
from scipy.optimize import minimize

def solve():
    dev = qml.device("default.qubit", wires=2)
    h = qml.Hamiltonian([1., .5, .7], [qml.Z(0), qml.Z(1), qml.X(0) @ qml.X(1)])
    @qml.qnode(dev)
    def energy(theta):
        qml.RY(theta[0], wires=0)
        qml.RY(theta[1], wires=1)
        qml.CNOT(wires=[0,1])
        return qml.expval(h)
    results = [minimize(energy, x, method="BFGS") for x in ([.1,.2],[3.,.2],[.2,3.],[3.,3.])]
    value = min(float(x.fun) for x in results)
    exact = float(np.linalg.eigvalsh(qml.matrix(h, wire_order=[0,1]))[0])
    return {"energy":value,"exact":exact,"gap":value-exact}
