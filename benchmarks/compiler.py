import json
from quantum_engine.compiler import benchmark
from quantum_engine.error_control import mitigate, bit_flip_code

if __name__ == "__main__":
    print(json.dumps({"compiler":benchmark(),"readout_corrected":mitigate([.9,.1],.1).tolist(),"bit_flip_fidelities":[bit_flip_code(i) for i in range(3)]},indent=2))
