import time
from line_profiler import LineProfiler


def slow_function():
    time.sleep(2)
    return sum(i ** 2 for i in range(10000))


def optimized_fast_function():
    return sum(i ** 2 for i in range(100))


def memory_intensive_function():
    return sum(i ** 2 for i in range(10000000))


def main():
    slow_function()
    optimized_fast_function()
    memory_intensive_function()


def profile_main():
    profiler = LineProfiler()
    profiler.add_function(slow_function)
    profiler.add_function(optimized_fast_function)
    profiler.add_function(memory_intensive_function)
    profiler.runcall(main)
    profiler.print_stats()


if __name__ == "__main__":
    profile_main()
