import unittest
from cpu_engine.core import benchmark

class TestCPU(unittest.TestCase):
    def test_reproducibility(self):
        a = benchmark(8, 2)
        b = benchmark(8, 2)
        self.assertAlmostEqual(a["checksum"], b["checksum"])
        self.assertGreater(a["median_seconds"], 0)
        self.assertGreater(a["gflops"], 0)

    def test_invalid_size(self):
        with self.assertRaises(ValueError):
            benchmark(0)
