import threading
import time

def wait(time_sec):
    print("sleep", time_sec)
    time.sleep(time_sec)
    print("done",time_sec)

t1 = threading.Thread(target=wait, args=(3,))
t2 = threading.Thread(target=wait, args=(2,))

t1.start()
t2.start()

t1.join()
print("We're all done1")
t2.join()

print("We're all done2")
