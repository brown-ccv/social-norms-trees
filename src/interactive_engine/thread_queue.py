import random
import threading
import queue
import time

tasks = queue.Queue()


def worker(id, report):
    while True:
        item = tasks.get()
        report(f"{id=:2} start  {item=:2} {time.strftime('%X')}")
        time.sleep(random.choice([0.1, 0.1, 1, 2, 3]))
        report(f"{id=:2} finish {item=:2} {time.strftime('%X')}")
        tasks.task_done()


def make_message_queue_and_reporter():
    messages = queue.Queue()

    def reporter():
        while True:
            message = messages.get()
            print(message)
            messages.task_done()

    def reporter_callback(message):
        messages.put(message)

    return messages, reporter, reporter_callback


_, reporter, reporter_callback = make_message_queue_and_reporter()
threading.Thread(target=reporter, daemon=True).start()

# Turn-on the worker thread.
for i in range(10):
    threading.Thread(
        target=worker, daemon=True, kwargs=dict(id=i, report=reporter_callback)
    ).start()


# Send thirty task requests to the worker.
for item in range(100):
    tasks.put(item)

# Block until all tasks are done.
tasks.join()


print("\nDone")
