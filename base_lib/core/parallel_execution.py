import os
from dataclasses import dataclass, field
import concurrent.futures
from typing import Callable, Any, Optional, Union


@dataclass
class ParallelExecutor:
    max_workers: Optional[int] = None  # Optional max workers limit
    executor: Optional[Union[concurrent.futures.ThreadPoolExecutor, concurrent.futures.ProcessPoolExecutor]] = field(
        init=False, default=None)

    def __enter__(self):
        """ Initialize the executor in the subclass. """
        raise NotImplementedError("Subclasses must implement this method.")

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ Shuts down the executor gracefully. """
        if self.executor:
            self.executor.shutdown(wait=True)

    def execute(self, func: Callable, *args: Any, **kwargs: Any):
        """ Submits a function to the executor for parallel execution. """
        if self.executor is None:
            raise RuntimeError("Executor not initialized. Use within a context manager.")
        future = self.executor.submit(func, *args, **kwargs)
        return future

    def map(self, func: Callable, iterable):
        """ Executes the function over the iterable in parallel. """
        if self.executor is None:
            raise RuntimeError("Executor not initialized. Use within a context manager.")
        return self.executor.map(func, iterable)
import threading

@dataclass
class ThreadParallelExecutor(ParallelExecutor):
    lock: threading.Lock = field(init=False, default_factory=threading.Lock)

    def __enter__(self):
        """ Initialize the thread pool executor. """
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)
        return self
import multiprocessing

@dataclass
class ProcessParallelExecutor(ParallelExecutor):
    lock: multiprocessing.Lock = field(init=False, default_factory=multiprocessing.Lock)

    def __enter__(self):
        """ Initialize the process pool executor. """
        self.executor = concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers)
        return self


def sample_task(x):
    print(threading.get_ident())
    return x * x


if __name__ == '__main__':

    # exe = ProcessParallelExecutor(max_workers=4)
    # res = exe.map(sample_task, range(10))
    # print(list(res))
    # Using multithreading
    with ThreadParallelExecutor(max_workers=4) as executor:
        results = executor.map(sample_task, range(10))
        print("Threading results:", list(results))

    # Using multiprocessing
    with ProcessParallelExecutor(max_workers=4) as executor:
        results = executor.map(sample_task, range(10))
        print("Multiprocessing results:", list(results))
