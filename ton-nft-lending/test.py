from threading import Thread
import time

def f(x):
    txt = "sleep " + str(x)
    print(txt)
    time.sleep(x)
    print("done " + txt)



Thread(target=f, args=[3]).start()
Thread(target=f, args=[2]).start()
Thread(target=f, args=[1]).start()



