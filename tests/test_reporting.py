import csv
import json
import pytest
from benchmarks.report import summarize, export

def test_report(tmp_path):
    r=summarize("cpu","matrix",[{"median_seconds":1},{"median_seconds":3}],3600)
    assert r["median_seconds"]==2
    assert r["throughput_jobs_per_second"]==.5
    assert r["estimated_cost_usd_per_job"]==2
    export([r],tmp_path)
    assert json.loads((tmp_path/"results.json").read_text())["results"]==[r]
    with (tmp_path/"results.csv").open() as f:
        assert len(list(csv.DictReader(f)))==1

def test_invalid():
    with pytest.raises(ValueError):
        summarize("cpu","matrix",[{"median_seconds":0},{"median_seconds":1}])
