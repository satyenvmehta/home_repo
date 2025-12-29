
import logging
from fastapi import BackgroundTasks

# Set up logging configuration
logging.basicConfig(level=logging.INFO)

class TryCatchFinally:
    def __init__(self, run, finally_block):
        self.run = run
        self.finally_block = finally_block
        self.result = None

    async def execute(self, *args, **kwargs):
        try:
            # Asynchronously execute the main function
            logging.info("Task is running...")
            self.result = await self.run(*args, **kwargs)
        except Exception as e:
            # Handle exception (log or do something here)
            logging.error(f"Error occurred in task: {e}")
        finally:
            # Always execute the finally block (can also be async)
            logging.info("Executing final cleanup...")
            await self.finally_block()

# Wrapper function that adds logging and error handling via TryCatchFinally
def add_task_with_logging(background_tasks: BackgroundTasks, task_function, finally_block, *args, **kwargs):
    # Log task details
    logging.info(f"Adding task: {task_function.__name__}")
    logging.info(f"Arguments: {args}")
    logging.info(f"Keyword Arguments: {kwargs}")

    # Define an async wrapped task that uses TryCatchFinally for error handling and logging
    async def wrapped_task(*args, **kwargs):
        try_catch = TryCatchFinally(
            run=task_function,
            finally_block=finally_block
        )
        await try_catch.execute(*args, **kwargs)

    # Add the wrapped task to the background tasks
    background_tasks.add_task(wrapped_task, *args, **kwargs)

    # Log task added successfully
    logging.info(f"Task {task_function.__name__} added successfully.")

# Example async background task function
async def some_background_task(param1: str, param2: int):
    # Simulate async task logic with potential for raising an exception
    logging.info(f"Executing background task with {param1} and {param2}")
    if param2 == 0:
        raise ValueError("param2 cannot be zero")

# Example async 'finally' block function
async def final_cleanup():
    logging.info("Final cleanup executed.")

from fastapi import FastAPI

app = FastAPI()

@app.get("/run-task/")
async def run_task(param1: str, param2: int, background_tasks: BackgroundTasks):
    # Use the wrapper with TryCatchFinally and logging to add the background task
    add_task_with_logging(background_tasks, some_background_task, final_cleanup, param1, param2)
    return {"message": "Background task added with logging and TryCatchFinally"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
#     logging.info("Server started at XXXXXXXXXXXXXXXXXXX")
