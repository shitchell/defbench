'''
Run tests on methods to determine execution time
and memory usage. Keeps a history of all tests
run for later review and analysis.

example:
```
import defbench

def for_loop(counter=5):
    for i in range(counter):
        continue

f = defbench.run(for_loop)
print(f)
```
'''

import sys
import timeit
from io import StringIO
from typing import Callable, List
from memory_profiler import memory_usage

class TestRunningException(Exception): pass

class TestRun:
    '''
    Represents the results after running a benchmark test. Contains information
    about the name of the function ran, average time for completion, and average
    memory usage.
    '''
    _func: Callable
    _mem: List[float]
    __mem_raw: List[float]
    name: str
    time: float
    stdout: str
    stderr: str
    repeat: int

    def __init__(self, func: Callable, name: str = None, repeat: int = 1, memory: List[float] = [], time: float = 0.0, stdout: str = "", stderr: str = ""):
        self._func = func
        if name:
            self.name = name
        else:
            try:
                self.name = func.__code__.co_name
            except:
                self.name = "<function>"
        self.repeat = repeat
        self._mem_raw = memory
        self.time = time
        self.stdout = stdout
        self.stderr = stderr
        history.add(self)

    @property
    def _mem_raw(self) -> List[float]:
        return self.__mem_raw

    @_mem_raw.setter
    def _mem_raw(self, values: List[float]):
        # make sure the correct type is used
        if not isinstance(values, list):
            raise TypeError('Memory values must be of type List[float]')
        
        # keep a copy of the raw memory data
        self.__mem_raw = values
        
        # and normalize what we'll *actually* use
        if values:
            initial = values[0]
            self._mem = [x - initial for x in values]
        else:
            self._mem = []

    @property
    def func(self) -> Callable:
        return self._func

    @property
    def memory(self) -> float:
        if self._mem:
            return max(self._mem)
        return None
    
    def __str__(self) -> str:
        output = f"<TestRun '{self.name}'\n"
        output += f'    runs:         {self.repeat:,}\n'
        output += f'    avg time: {self.time:.4}s\n'
        output += f'    avg mem:    {self.memory:.4}Mib>'
        return output
    
    def __repr__(self) -> str:
        return f'TestRun(name="{self.name}" time={self.time:.4} mem={self.memory})'

class history:
    '''
    Keeps a record of all TestRuns created by either the module level `.run()`
    method or `Test.run()`. Provides methods for retrieving information about
    previous TestRuns, optionally based on filters.
    '''
    _history: List[TestRun] = []

    @staticmethod
    def average_time(filter: Callable = None) -> float:
        '''
        Return the average time for all TestRuns in the history. Optionally,
        pass a function which accepts a single argument to filter results
        (see `.get()`)
        '''
        runs = history.get(filter)
        total = sum([r.time for r in runs])
        return total / len(runs)

    @staticmethod
    def average_memory(filter: Callable = None) -> float:
        '''
        Return the average memory usage (MiB) for all TestRuns in the history.
        Optionally, pass a function which accepts a single argument to filter
        results (see `.get()`)
        '''
        runs = history.get(filter)
        total = sum([r.memory for r in runs])
        return total / len(runs)

    @staticmethod
    def add(run: TestRun) -> None:
        if isinstance(run, TestRun):
            history._history.append(run)

    @staticmethod
    def get(filter: Callable = None) -> List[TestRun]:
        '''
        Return all TestRuns from the history. Optionally, pass a function that
        accepts a single argument to filter results, e.g.:

        ```
        history.get(lambda x: x.name.endswith('_loop'))
        history.get(lambda x: x.time > 10))
        ```
        '''
        if filter:
            return [x for x in history._history if filter(x)]
        return history._history

class Test:
    '''
    Class used for running tests on a function. Stores the function to use along
    with default values for each test. Tests can be run using `.run()`, and each
    test is available via the `.history` attribute.
    '''
    _func: Callable
    _repeat: int
    _running: bool
    name: str
    history: List[TestRun]

    def __init__(self, func: Callable, repeat: int = 10, name: str = None):
        self._func = func
        self.name = name
        self._repeat = repeat
        self._running = False
        self.history = []
    
    def _run(self, repeat: int, name: str) -> None:
        # create new test instance
        test_run = TestRun(self._func, repeat=repeat, name=name)

        # store the normal output file descriptors...
        old_stdout = sys.stdout
        old_stderr = sys.stderr

        # ...so that we can redirect all output for ourselves
        sys.stdout = StringIO()
        sys.stderr = StringIO()

        # run the function
        try:
            test_run.time = timeit.timeit(self._func, number=repeat)
        except Exception as e:
            # return stdout back to normal before passing the error
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            raise e

        # get output of the function from our fake variable
        test_run.stdout = sys.stdout.getvalue()
        test_run.stderr = sys.stderr.getvalue()

        # put the screen output back to normal
        sys.stdout = old_stdout
        sys.stderr = old_stderr

        self.history.append(test_run)

    def run(self, repeat: int = 100, name: str = None) -> TestRun:
        '''
        Run the test function `repeat` times. Returns a TestRun with memory
        and timing information, and adds the TestRun to `Test.history`.
        '''
        # don't run again while already running
        if self._running:
            raise TestRunningException(f'Test "{self._func.__code__.co_name}" already running')

        self._running = True
        mem_usage = None
        name = name or self.name

        try:
            mem_usage = memory_usage((self._run, (repeat,name)), interval=0.05)
        except Exception as e:
            # reset _running status before passing the error
            self._running = False
            raise e
        
        test_run = self.history[-1]
        test_run._mem_raw = mem_usage
        history.add(test_run)
        return test_run
    
    @property
    def last(self) -> TestRun:
        return self.history[-1]

def run(func: Callable, repeat: int = 10, name: str = None) -> TestRun:
    '''
    Run a function `repeat` times, returning a TestRun instance with average
    time and memory usage. Also adds the TestRun to the module's history for
    later use.
    '''
    test_run = Test(func, repeat=repeat, name=name)
    return test_run.run(repeat)
