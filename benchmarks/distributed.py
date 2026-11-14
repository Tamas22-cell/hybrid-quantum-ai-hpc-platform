import json
from distributed_engine.core import benchmark

if __name__ == "__main__":
    results=[benchmark(512,w) for w in (1,2)]
    for r in results:
        r["speedup"]=results[0]["median_seconds"]/r["median_seconds"]
        r["efficiency"]=r["speedup"]/r["workers"]
    print(json.dumps(results,indent=2))
