import threading
import time

def wait(time_sec):
    print("sleep", time_sec)
    time.sleep(time_sec)
    print("done")

thread1 = threading.Sleep(target=wait, args=(2))
