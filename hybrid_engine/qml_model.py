import pennylane as qml
import torch

def train():
    torch.manual_seed(42)
    dev = qml.device("default.qubit", wires=2)
    @qml.qnode(dev, interface="torch")
    def circuit(x,w):
        qml.RY(x[0], wires=0)
        qml.RY(x[1], wires=1)
        qml.RY(w[0], wires=0)
        qml.RY(w[1], wires=1)
        qml.CNOT(wires=[0,1])
        return qml.expval(qml.Z(1))
    x = torch.tensor([[0.,0.],[0.,3.14],[3.14,0.],[3.14,3.14]],dtype=torch.float64)
    y = torch.tensor([1.,-1.,-1.,1.],dtype=torch.float64)
    w = torch.tensor([.4,.3],dtype=torch.float64,requires_grad=True)
    opt = torch.optim.Adam([w],lr=.08)
    def loss():
        return ((torch.stack([circuit(v,w) for v in x])-y)**2).mean()
    initial = float(loss().detach())
    for _ in range(25):
        opt.zero_grad()
        loss().backward()
        opt.step()
    baseline = torch.cos(x[:,0])*torch.cos(x[:,1])
    return {"initial_loss":initial,"final_loss":float(loss().detach()),"classical_loss":float(((baseline-y)**2).mean())}
