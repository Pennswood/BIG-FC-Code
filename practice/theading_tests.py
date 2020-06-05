import threading
import time

def sample(ms):
    print("01")
    time.sleep(ms/1000)
    print("30")
def laser_fire():
    print("25")
    print("24")
t1 = threading.Thread(target=sample, args=(10,))
t2 = threading.Timer(0.0001, laser_fire)
t1.start()
t2.start()

