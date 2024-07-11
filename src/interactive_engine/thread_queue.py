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


class Robot:
    def __init__(self, id, report):
        self.queue = queue.Queue()
        self.id = id
        self.report = report

    def __call__(self, *args, **kwargs):
        tasks = self.queue
        report = self.report
        while True:
            item = tasks.get()
            _logger.debug(f"{self.id} start {item=} {time.strftime('%X')}")
            match item:
                case Task(kind="move to", value=place):
                    _logger.debug(f"{self.id} moving to {place=}")
                    time.sleep(random.choice([0.1, 0.1, 1, 2, 3]))
                case Task(kind="announce", value=message):
                    time.sleep(random.choice([0.1, 0.1, 1, 2, 3]))
                    report(f"{self.id}: '{message}'")
            _logger.debug(f"{self.id} finish {item=} {time.strftime('%X')}")
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
robot = Robot(
    id="robbie",
    report=reporter_callback,
)
threading.Thread(
    target=robot,
    daemon=True,
).start()


@dataclass
class Task:
    kind: str
    value: Optional[str] = None


# Send thirty task requests to the worker.
robot.queue.put(Task("move to", "A"))
robot.queue.put(Task("move to", "B"))
robot.queue.put(Task("move to", "C"))
robot.queue.put(Task("announce", "I'm starting again"))
robot.queue.put(Task("move to", "A"))

# Block until all tasks are done.
robot.queue.join()


print("\nDone")
