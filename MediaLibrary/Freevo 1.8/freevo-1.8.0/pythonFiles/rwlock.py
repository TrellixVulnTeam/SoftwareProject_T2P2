"""Simple reader-writer locks in Python
Many readers can hold the lock XOR one and only one writer"""
import threading

version = """$Id: rwlock.py 10118 2007-11-14 20:23:21Z duncan $"""

class RWLock:
    """
  A simple reader-writer lock Several readers can hold the lock
  simultaneously, XOR one writer. Write locks have priority over reads to
  prevent write starvation.
  """
    def __init__(self):
        self.rwlock = 0
        self.writers_waiting = 0
        self.monitor = threading.Lock()
        self.readers_ok = threading.Condition(self.monitor)
        self.writers_ok = threading.Condition(self.monitor)
    def acquire_read(self):
        """Acquire a read lock. Several threads can hold this typeof lock.
    It is exclusive with write locks."""
        self.monitor.acquire()
        while self.rwlock < 0 or self.writers_waiting:
            self.readers_ok.wait()
        self.rwlock += 1
        self.monitor.release()
    def acquire_write(self):
        """Acquire a write lock. Only one thread can hold this lock, and
    only when no read locks are also held."""
        self.monitor.acquire()
        while self.rwlock != 0:
            self.writers_waiting += 1
            self.writers_ok.wait()
            self.writers_waiting -= 1
        self.rwlock = -1
        self.monitor.release()
    def promote(self):
        """Promote an already-acquired read lock to a write lock
        WARNING: it is very easy to deadlock with this method"""
        self.monitor.acquire()
        self.rwlock -= 1
        while self.rwlock != 0:
            self.writers_waiting += 1
            self.writers_ok.wait()
            self.writers_waiting -= 1
        self.rwlock = -1
        self.monitor.release()
    def demote(self):
        """Demote an already-acquired write lock to a read lock"""
        self.monitor.acquire()
        self.rwlock = 1
        self.readers_ok.notifyAll()
        self.monitor.release()
    def release(self):
        """Release a lock, whether read or write."""
        self.monitor.acquire()
        if self.rwlock < 0:
            self.rwlock = 0
        else:
            self.rwlock -= 1
        wake_writers = self.writers_waiting and self.rwlock == 0
        wake_readers = self.writers_waiting == 0
        self.monitor.release()
        if wake_writers:
            self.writers_ok.acquire()
            self.writers_ok.notify()
            self.writers_ok.release()
        elif wake_readers:
            self.readers_ok.acquire()
            self.readers_ok.notifyAll()
            self.readers_ok.release()

if __name__ == '__main__':
    import time
    rwl = RWLock()
    class Reader(threading.Thread):
        def run(self):
            print self, 'start'
            rwl.acquire_read()
            print self, 'acquired'
            time.sleep(5)
            print self, 'stop'
            rwl.release()
    class Writer(threading.Thread):
        def run(self):
            print self, 'start'
            rwl.acquire_write()
            print self, 'acquired'
            time.sleep(10)
            print self, 'stop'
            rwl.release()
    class ReaderWriter(threading.Thread):
        def run(self):
            print self, 'start'
            rwl.acquire_read()
            print self, 'acquired'
            time.sleep(5)
            rwl.promote()
            print self, 'promoted'
            time.sleep(5)
            print self, 'stop'
            rwl.release()
    class WriterReader(threading.Thread):
        def run(self):
            print self, 'start'
            rwl.acquire_write()
            print self, 'acquired'
            time.sleep(10)
            print self, 'demoted'
            rwl.demote()
            time.sleep(10)
            print self, 'stop'
            rwl.release()
    Reader().start()
    time.sleep(1)
    Reader().start()
    time.sleep(1)
    ReaderWriter().start()
    time.sleep(1)
    WriterReader().start()
    time.sleep(1)
    Reader().start()
