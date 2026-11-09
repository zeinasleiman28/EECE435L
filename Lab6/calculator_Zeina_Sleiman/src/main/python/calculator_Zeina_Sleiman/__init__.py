"""calculator_Zeina_Sleiman - simple calculator package built with PyBuilder.

EECE 435L - Lab 6 - Zeina Sleiman
"""
import math


def add(x, y):
    return x + y


def subtract(x, y):
    return x - y


def multiply(x, y):
    return x * y


def divide(x, y):
    if y == 0:
        raise ValueError("Cannot divide by zero.")
    return x / y


# ---- Graded exercise: new functions ----

def modulus(x, y):
    """Remainder of x divided by y."""
    if y == 0:
        raise ValueError("Cannot compute modulus with zero divisor.")
    return x % y


def power(x, y):
    """x raised to the power y."""
    return x ** y


def square_root(x):
    """Square root of x (x must be >= 0)."""
    if x < 0:
        raise ValueError("Cannot compute square root of a negative number.")
    return math.sqrt(x)
