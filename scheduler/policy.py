"""Deterministic capability-aware scheduling; no external model required."""
def candidates(kind, size, gpu=False, distributed=False):
    if kind == "quantum":
        if not 2 <= size <= 20:
            raise ValueError("Invalid qubit count")
        return ["quantum_simulator"]
    if kind != "matrix" or not 1 <= size <= 2048:
        raise ValueError("Invalid workload")
    choices = []
    if gpu and size >= 512:
        choices.append("gpu")
    if distributed and size >= 1024:
        choices.append("ray")
    return choices + ["cpu"]
