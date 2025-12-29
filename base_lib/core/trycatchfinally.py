from typing import Callable, Any, Optional, Type

'''
Key Points:
__enter__/__exit__: These methods allow you to use the class within a with statement, mimicking the structure of a try-catch-finally block.
Parameterization: The class accepts the try_block, catch_block, and finally_block as callable functions, which you can define as needed.
Exception Handling: You can specify the type of exception to catch via the exception_type parameter (defaults to Exception).
This approach makes it easy to wrap any block of code with exception handling logic in a reusable and structured way.
'''

class TryCatchFinally_0:
    def __init__(
            self,
            try_block: Callable,
            catch_block: Optional[Callable[[Exception], Any]] = None,
            finally_block: Optional[Callable] = None,
            exception_type: Type[Exception] = Exception
    ):
        self.try_block = try_block
        self.catch_block = catch_block
        self.finally_block = finally_block
        self.exception_type = exception_type

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.try_block()
        except self.exception_type as e:
            if self.catch_block:
                self.catch_block(e)
        finally:
            if self.finally_block:
                self.finally_block()
        return True  # Prevents the exception from propagating


# Usage example
def try_logic():
    print("Executing try block")
    raise ValueError("An error occurred")


def handle_exception(e: Exception):
    print(f"Caught exception: {e}")


def final_logic():
    print("Executing finally block")


with TryCatchFinally_0(try_logic, handle_exception, final_logic):
    pass



'''
How it works:
You instantiate TryCatchFinally with the blocks you want for try, catch, and finally.
Call the run() method to execute the logic in sequence.
This approach doesn’t require a context manager (with statement) and gives a more traditional object-oriented style.
'''

class TryCatchFinally_v2:
    def __init__(self, try_block: Callable, catch_block: Optional[Callable[[Exception], Any]] = None, finally_block: Optional[Callable] = None):
        self.try_block = try_block
        self.catch_block = catch_block
        self.finally_block = finally_block

    def run(self):
        try:
            self.try_block()
        except Exception as e:
            if self.catch_block:
                self.catch_block(e)
        finally:
            if self.finally_block:
                self.finally_block()

'''
try_block: Callable – The function containing the primary logic to be executed.
catch_block: Callable[[Exception, Any], Any] (optional) – A function to handle exceptions. It receives the exception and the result (if available) from try_block.
finally_block: Callable[[Any], Any] (optional) – A function to execute after the try or catch blocks, usually for cleanup or final steps. It receives the result from try_block (if available).
result: Any – The value returned by the try_block. Available only after the run() method is called.
'''
from dataclasses import dataclass
from typing import Callable, Optional, Any

@dataclass
class TryCatchFinally:
    try_block: Callable
    catch_block: Optional[Callable[[Exception, Any], Any]] = None
    finally_block: Optional[Callable[[Any], Any]] = None
    result: Any = None  # To store the result of try_block

    def reset(self):
        self.result = None
        self.exception = False
        return

    def default_exception(self):
        print("Issue with process")
        self.exception = True
        return
    def default_finally(self):
        print("Finally")
        return
    def run(self, *args, **kwargs):
        try:
            self.reset()
            self.result = self.try_block(*args, **kwargs)  # Capture the return values (tuple or list)
        except Exception as e:
            if self.catch_block:
                self.catch_block(e, self.result, *args, **kwargs)  # Pass result to catch_block
            self.default_exception()
            return 
        finally:
            if self.finally_block:
                self.finally_block(self.result, *args, **kwargs)  # Pass result to finally_block
            self.default_finally()
            return

# Function to simulate the try block
def simple_try_logic(*args, **kwargs):
    print(f"Executing try logic with args: {args} and kwargs: {kwargs}")
    # Return multiple values as a tuple (e.g., sum, max, min of args)
    return sum(args), max(args), min(args)

def div_try_logic(n, d):
    print(f"Executing try logic with args: {n} and kwargs: {d}")
    # Return multiple values as a tuple (e.g., sum, max, min of args)
    return n/d

# Function to simulate the catch block
def simple_handle_exception(e, result=None, *args, **kwargs):
    print(f"Handling exception: {e}")
    if result:
        print(f"Partial result before exception: {result}")

# Function to simulate the finally block
def simple_final_logic(result=None, *args, **kwargs):
    print(f"Executing finally block with result: {result}")
    if result:
        sum_result, max_result, min_result = result
        print(f"Sum: {sum_result}, Max: {max_result}, Min: {min_result}")

# Using our TryCatchFinally class
tcf = TryCatchFinally(
    try_block=simple_try_logic,             # Pass the simple try logic function
    catch_block=simple_handle_exception,    # Pass the simple exception handler
    finally_block=simple_final_logic        # Pass the simple final logic
)

# Running the logic with parameters and collecting the result
tcf.run(10, 20, 30)

# Accessing the result directly
print(f"Try block result: {tcf.result}")

tcf = TryCatchFinally(
    try_block=div_try_logic,             # Pass the simple try logic function
    catch_block=None,    # Pass the simple exception handler
    finally_block=None        # Pass the simple final logic
)
tcf.run(3,2)
print( f"div_try_logic  : {tcf.result}")

tcf.run(3,0)
print( f"div_try_logic  : {tcf.result}")
