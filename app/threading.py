#threading example
import random
import time
import threading

def some_func(idx):

    inter = random.randint(0, 8)
    # print('>> %d' % idx)
    time.sleep(inter)
    print('%i sec >> %d >>' % (inter, idx))

if __name__ == "__main__":
    threads = []
    for idx in range(8):
        t = threading.Thread(target=some_func, args=(idx,))
        threads.append(t)
        print('starting %d' % idx)
        t.start()
    
    for t in enumerate(threads):
        t[1].join()
        print('ended %d' % t[0])