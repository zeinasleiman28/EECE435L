# Lab 9 – Profiling and Optimizing Python Code

Folder: [lab9_Zeina_Sleiman](lab9_Zeina_Sleiman/)

Profiles a small program (`slow_function`, `fast_function`, `memory_intensive_function`) with cProfile, line_profiler, memory_profiler, and unittest + coverage, then optimizes it and compares the results.

| Path | Content |
|---|---|
| `lab9_Zeina_Sleiman/original/` | Original code, profiler scripts, tests, `htmlcov/` |
| `lab9_Zeina_Sleiman/optimized/` | Loops replaced by `sum()` over generator expressions |
| `lab9_Zeina_Sleiman/results/` | Saved output of every run (`before_*` / `after_*`) |
| `lab9_Zeina_Sleiman/lab9_Zeina_Sleiman.docx` | Report with analysis and comparison table |

## Setup
```
cd Lab9/lab9_Zeina_Sleiman
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run (from `original/` or `optimized/`)
```
python -m cProfile -s tottime profiler.py
python profiler_lineprofiler.py
python profiler_memoryprofiler.py
coverage run -m unittest test_profiler.py
coverage report -m
coverage html
```

## Summary of results
- The optimized code is shorter (23 to 14 statements) and uses the same constant memory (about 28.5 MiB).
- It is **not faster**: the 10-million-element function takes 1.05 s vs 0.43 s un-profiled, and cProfile total goes from 2.56 s to 6.08 s because of generator-call overhead.
- memory_profiler's huge negative increments (e.g. -333520.5 MiB) are sums over millions of loop iterations and are not meaningful.
- Coverage: 90% before, 88% after; the same 4 lines (`main()` and the `__main__` guard) are never tested.
