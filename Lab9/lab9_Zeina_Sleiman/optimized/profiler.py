import time


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


if __name__ == "__main__":
    main()
