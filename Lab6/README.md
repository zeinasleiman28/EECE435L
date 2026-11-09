# Lab 6 – Automatic Build with PyBuilder

**EECE 435L – Software Tools Lab** · Zeina Sleiman

## What this is

`calculator_Zeina_Sleiman` is a small Python package built and tested with **PyBuilder** (`pyb`).
PyBuilder reads `build.py`, creates its own isolated venvs under `target/`, runs the unit tests, and reports a build summary.

```
calculator_Zeina_Sleiman/
├── build.py                                   <- PyBuilder build descriptor
├── src/main/python/calculator_Zeina_Sleiman/
│   └── __init__.py                            <- add, subtract, multiply, divide, modulus, power, square_root
└── tests/unittest/calculator_Zeina_Sleiman/
    └── test_calculator_Zeina_Sleiman.py       <- unittest cases for all 7 functions
```

## Graded exercise

Added `modulus(x, y)`, `power(x, y)` and `square_root(x)` plus their tests (including the error cases: modulus by zero and square root of a negative number).

## Run

```powershell
cd Lab6\calculator_Zeina_Sleiman
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
pip install pybuilder
pyb run_unit_tests
```

Expected: `All unit tests passed.` → `BUILD SUCCESSFUL` → `Build finished at …` with the base directory ending in `calculator_Zeina_Sleiman`.

Plain unittest (without PyBuilder):

```powershell
python -m unittest tests.unittest.calculator_Zeina_Sleiman.test_calculator_Zeina_Sleiman
```

## Note on `build.py`

The lab sheet's `build.py` sets `unittest_module = "tests.unittest"`, but PyBuilder's unittest plugin actually looks for tests in `dir_source_unittest_python` (default `src/unittest/python`). Since the lab puts tests under `tests/unittest/calculator_Zeina_Sleiman/`, `build.py` points that property there so `pyb run_unit_tests` discovers `test_*.py`.
