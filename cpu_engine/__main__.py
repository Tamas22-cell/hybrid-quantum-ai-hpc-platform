import argparse
import json
from .core import benchmark

parser = argparse.ArgumentParser()
parser.add_argument("--size", type=int, default=256)
parser.add_argument("--repeats", type=int, default=5)
args = parser.parse_args()
print(json.dumps(benchmark(args.size, args.repeats), indent=2))
