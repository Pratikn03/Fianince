# CPU execution record

The original full serial extended search was started in the isolated staging
copy. A separate wrapper distributes the 400 independent least-squares starting
points across eight CPU workers. It preserves the serial random-draw order,
solver settings, returned order, and duplicate-filtering rule. Numerical
outcomes are not selected by whether they favor uniqueness.

The first wrapper used `runpy` with the name `__main__`. On macOS, spawned workers
then re-entered the serial driver. That startup attempt was terminated, and its
partial log is retained as `parallel_global_search_startup_failure.log`; it is
not a completed search. The corrected wrapper uses a separate run name so the
worker functions remain importable from the wrapper module. The final validation
receipt identifies the completed output actually used.

These SciPy least-squares solves and the Lean checks use CPUs. They do not have a
GPU backend, and no GPU acceleration is claimed.
