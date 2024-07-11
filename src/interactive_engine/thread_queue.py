import random
import threading
import queue
import time

tasks = queue.Queue()


def worker(id, message_queue):
    while True:
        item = tasks.get()
        message_queue.put(f"{id=} start  {item=:2} {time.strftime('%X')}")
        time.sleep(random.choice([0.1, 0.1, 1, 2, 3]))
        message_queue.put(f"{id=} finish {item=:2} {time.strftime('%X')}")
        tasks.task_done()


messages = queue.Queue()


def reporter():
    while True:
        message = messages.get()
        print(message)
        messages.task_done()


# Turn-on the worker thread.
threading.Thread(target=worker, daemon=True, args=(0, messages)).start()
threading.Thread(target=worker, daemon=True, args=(1, messages)).start()
threading.Thread(target=worker, daemon=True, args=(3, messages)).start()
threading.Thread(target=reporter, daemon=True).start()

# Send thirty task requests to the worker.
for item in range(100):
    tasks.put(item)

# Block until all tasks are done.
tasks.join()


print("\n\nAll work completed")
