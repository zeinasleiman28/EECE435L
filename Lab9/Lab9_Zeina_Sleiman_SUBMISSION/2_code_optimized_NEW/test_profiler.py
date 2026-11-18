import time
import unittest

import memory_profiler

from profiler import slow_function, optimized_fast_function, memory_intensive_function


class TestProfiler(unittest.TestCase):
    def time_function(self, func):
        start_time = time.time()
        func()
        end_time = time.time()
        return end_time - start_time

    def test_slow_function(self):
        duration = self.time_function(slow_function)
        print(f"slow_function duration: {duration:.4f} s")
        self.assertGreater(duration, 2)

    def test_optimized_fast_function(self):
        duration = self.time_function(optimized_fast_function)
        print(f"optimized_fast_function duration: {duration:.6f} s")
        self.assertLess(duration, 1)

    def test_memory_intensive_function(self):
        memory_before = memory_profiler.memory_usage()[0]
        duration = self.time_function(memory_intensive_function)
        memory_after = memory_profiler.memory_usage()[0]
        print(f"memory_intensive_function duration: {duration:.4f} s")
        print(f"memory before: {memory_before:.2f} MiB, after: {memory_after:.2f} MiB")
        self.assertLess(duration, 5)
        self.assertGreater(memory_after, memory_before)


if __name__ == "__main__":
    unittest.main()
