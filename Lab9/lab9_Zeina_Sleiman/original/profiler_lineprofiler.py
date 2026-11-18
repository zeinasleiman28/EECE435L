import time
from line_profiler import LineProfiler


def slow_function():
    time.sleep(2)
    total = 0
    for i in range(10000):
        total += i ** 2
    return total


def fast_function():
    total = 0
    for i in range(100):
        total += i ** 2
    return total


def memory_intensive_function():
    total = 0
    for i in range(10000000):
        total += i ** 2
    return total


def main():
    slow_function()
    fast_function()
    memory_intensive_function()


def profile_main():
    profiler = LineProfiler()
    profiler.add_function(slow_function)
    profiler.add_function(fast_function)
    profiler.add_function(memory_intensive_function)
    profiler.runcall(main)
    profiler.print_stats()


if __name__ == "__main__":
    profile_main()
