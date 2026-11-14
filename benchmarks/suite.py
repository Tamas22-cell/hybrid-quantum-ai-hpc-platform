import argparse
from benchmarks.report import summarize, export
from cpu_engine.core import benchmark as cpu
from quantum_engine.core import benchmark as quantum
from gpu_engine.core import benchmark as gpu

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",default="benchmark-results")
    p.add_argument("--gpu",action="store_true")
    p.add_argument("--hourly-rate",type=float,default=None)
    args=p.parse_args()
    jobs=[("cpu","matrix_256",lambda:cpu(256,3)),("qiskit","ghz_4",lambda:quantum(4,3))]
    if args.gpu:
        jobs.append(("cuda","matrix_256",lambda:gpu(256,3)))
    rows=[summarize(name,workload,[run() for _ in range(5)],args.hourly_rate) for name,workload,run in jobs]
    if args.gpu:
        rows[-1]["compute_speedup"]=rows[0]["median_seconds"]/rows[-1]["median_seconds"]
    export(rows,args.output)

if __name__=="__main__":
    main()
