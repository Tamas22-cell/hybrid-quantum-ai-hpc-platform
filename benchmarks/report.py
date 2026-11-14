"""Repeated benchmark aggregation and portable exports."""
import csv
import json
import math
import platform
from pathlib import Path
from datetime import datetime, timezone
import numpy as np

def summarize(name, workload, samples, hourly_rate=None):
    times=np.asarray([x["median_seconds"] for x in samples],dtype=float)
    if len(times)<2 or not np.all(np.isfinite(times)) or np.any(times<=0):
        raise ValueError("At least two positive finite measurements required")
    if hourly_rate is not None and (not math.isfinite(hourly_rate) or hourly_rate<0):
        raise ValueError("Invalid hourly rate")
    median=float(np.median(times))
    result={"backend":name,"workload":workload,"runs":len(times),
            "median_seconds":median,"p95_run_median_seconds":float(np.percentile(times,95)),
            "throughput_jobs_per_second":1/median,
            "estimated_cost_usd_per_job":None if hourly_rate is None else hourly_rate*median/3600}
    for key in ("fidelity","gflops","max_abs_error"):
        if all(key in x for x in samples):
            result[key]=float(np.median([x[key] for x in samples]))
    return result

def export(rows, directory):
    target=Path(directory)
    target.mkdir(parents=True,exist_ok=True)
    metadata={"timestamp":datetime.now(timezone.utc).isoformat(),"platform":platform.platform(),"python":platform.python_version(),"numpy":np.__version__}
    (target/"results.json").write_text(json.dumps({"metadata":metadata,"results":rows},indent=2,allow_nan=False))
    fields=sorted(set().union(*(row.keys() for row in rows)))
    with (target/"results.csv").open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
