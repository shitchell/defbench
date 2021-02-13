defbench.py
===

a python3 module for easily benchmarking the elapsed time and memory usage of python functions


## quick start
make sure you have the requirements (currently just *memory-profiler*) installed:

```sh
pip install -r requirements.txt
```

1. import defbench
2. define a function to test
3. use `defbench.run(func[, repeat][, name])`

```python
import defbench

def search_list():
  "two" in ["one", "two", "three"]

results = defbench.run(search_list, repeat=1000)
print(results)
```
*outputs*
```
<TestRun 'search_list'
  runs:     1,000
  avg time: 0.0002124s
  avg mem:  0.0Mib>
```

## defbench.run()
this is the easiest way to use this tool. it generates a `TestRun` object, returns it, and adds it to `defbench.history` for later review or analysis.

```python
run(func: Callable, repeat: int = 10, name: str = None) -> TestRun
```
pass in the function to be tested. optionally, specify the number of times to repeat the function and the name to use. if a name is not provided, it defaults to the function name ("&lt;lambda>" for lambda functions)

## TestRun
a `TestRun` object is returned by either `defbench.run()` or `defbench.Test.run()`. it contains all of the results from benchmarking a function.

### attributes
| attribute | type | description |
| --------- | ---- | ----------- |
| _mem_raw  | List[float] | raw slices of the *entire* program's memory usage (MiB) over the course of every repeated call as returned by *memory-profiler* |
| _mem      | List[float] | _mem_raw "normalized" (initial program memory usage subtracted from all memory usage values) |
| func      | Callable    | the benchmarked function | 
| name      | str         | the function name *or* the name passed with `.run(func, name="foobar")` |
| time      | float       | the average time (seconds) of all runs |
| memory    | float       | the peak memory usage (MiB) |
| stdout    | str         | output is suppressed by `.run()` and stored here for later retrieval |
| repeat    | int         | number of tests run |

### initialization
```python
__init__(self,
    func: Callable,
    name: str = None,
    repeat: int = 1,
    mem: List[float] = [],
    time: float = 0.0,
    stdout: str = ""
)
```

a `TestRun` object is *not* meant to be initialized on its own! it is meant to be generated by either `defbench.Test.run()` or `defbench.run()`

### measuring memory
i want to explain how memory measurement with *memory-profiler* (and thus defbench) works since it took me a minute to understand. essentially, it captures the *entire* program's memory usage at specified intervals (0.01s for now, although i might tweak that and/or let the interval be set). when profiling a specific function, it still grabs the *entire* program's memory usage; it just does so for the duration that the function is running. i.e.:

1. your python script starts up -- 1MiB -- 1MiB total
2. you create some lists and do some stuff -- 3MiB -- 4MiB total
3. you use `defbench.run(my_function)` -- 2MiB -- 6MiB total

so when `defbench.run(my_function)` is called, *memory-profiler* will report **4.0** as the initial memory usage slice and **6.0** as the peak memory slice (e.g.: `[4.0, 4.3, 4.9, 5.5, 6.0]`). this is what's stored in `TestRun._mem_raw`. however, we don't really care about the rest of the program, so we subtract the initial value from all subsequent memory usage slices (e.g.: `[0.0, 0.3, 0.9, 1.5, 2.0]`). this is what's stored in `TestRun._mem`. but since all most users *really* care about is the peak usage, that's what's returned by `TestRun.memory` (**2.0** in our example).

and just to be totally clear, `max()` is used to find the peak memory usage slice. so even if some objects get released from memory throughout your function, and the last memory usage slice is lower than the peak (e.g.: `[0.0, 0.5, 1.0, 0.8]`), the maximum value is still returned by `TestRun.memory` (e.g.: **1.0**).

### stdout
during a `.run()` call, all output to `sys.stdout` (e.g. `print()` statements) is temporarily redirected so that output can be captured. you can access it later using `TestRun.stdout`

## Test

a `Test` object is initialiezd with a function name and some default values. calling `Test.run()` will add a new `TestRun` object to `Test.history` and `defbench.history` and then return it.

### attributes
| attribute | type | description |
| --------- | ---- | ----------- |
| _func     | Callable      | the benchmarked function |
| _repeat   | int           | the default number of times to run the function |
| _running  | bool          | boolean representing if this `Test` is currently running |
| name      | str           | the default name to use for tests |
| history   | List[TestRun] | all `TestRun`s generated by `Test.run()` |

### methods
```python
run(repeat: int = 100, name: str = None) -> TestRun
```
returns a new `TestRun` and appends it to `Test.history`. optionally, set the number of times to run repeat the test and the name to use for this `TestRun`.

### default values priority
priority for name/repeat values used are:

1. value passed in to `Test.run()` or `defbench.run()`
2. value passed to `__init__()` (or `Test()`) during initialization
3. (for name only) function name if neither above provided
4. default value (10 for repeat and "&lt;function>" for function names, but i'm not sure a function can even *not* have a name 99% of the time... still, it's there just in case someone does some weird code compiling voodoo)

## history
there's a history object at the module level (`defbench.history`) that contains a history of every `TestRun` object (each instance is added in `TestRun.__init__`).

### attributes
| attribute | type | description |
| --------- | ---- | ----------- |
| _history  | List[TestRun] | all `TestRun` objects |

### methods
```python
average_time(filter: Callable = None) -> float
```
return the average time of all `TestRun`s. optionally, pass a function to be used as a filter, e.g.: `history.average_time(lambda x: x.name == "str_list_test")`

```python
average_memory(filter: Callable = None) -> float
```
get the average memory usage in *MiB* of all `TestRun`s. optionally, pass a function to be used as a filter, e.g.: `history.average_memory(lambda x: x.stdout.contains("hello world")`

```python
add(run: TestRun) -> None
```
add a `TestRun` to the module level history

```python
get(filter: Callable = None) -> List[TestRun]
```
return all `TestRun` objects in history. optionally, pass a function to be used as a filter, e.g.: `history.get(lambda x: x.time > 30)`

# todo
- [ ] create a generic `_history` class to be used at the module level and by instances of `Test`
- [ ] add more analysis options for items in `history`
- [ ] capture `stderr` in `TestRun.run()`?
- [ ] add to pip
