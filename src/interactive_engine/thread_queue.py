import logging
import random
import threading
import queue
import time
from dataclasses import dataclass
from typing import Optional

tasks = queue.Queue()
_logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)


def worker(id, report):
    while True:
        item = tasks.get()
        _logger.debug(f"{id=:2} start  {item=} {time.strftime('%X')}")
        match item:
            case Task(kind="move to", value=place):
                _logger.debug(f"{id=:2} moving to {place=}")
                time.sleep(random.choice([0.1, 0.1, 1, 2, 3]))
            case Task(kind="announce", value=message):
                time.sleep(random.choice([0.1, 0.1, 1, 2, 3]))
                report(f"{id=:2}: '{message}'")
        _logger.debug(f"{id=:2} finish {item=} {time.strftime('%X')}")
        tasks.task_done()


def make_message_queue_and_reporter():
    message_queue = queue.Queue()

    def reporter():
        while True:
            message = message_queue.get()
            print(message)
            message_queue.task_done()

    def reporter_callback(message):
        message_queue.put(message)

    return message_queue, reporter, reporter_callback


_, reporter, reporter_callback = make_message_queue_and_reporter()
threading.Thread(target=reporter, daemon=True).start()

# Turn-on the worker thread.
for i in range(1):
    threading.Thread(
        target=worker, daemon=True, kwargs=dict(id=i, report=reporter_callback)
    ).start()


@dataclass
class Task:
    kind: str
    value: Optional[str] = None


# Send thirty task requests to the worker.
tasks.put(Task("move to", "A"))
tasks.put(Task("move to", "B"))
tasks.put(Task("move to", "C"))
tasks.put(Task("announce", "I'm starting again"))
tasks.put(Task("move to", "A"))

# Block until all tasks are done.
tasks.join()


print("\nDone")
