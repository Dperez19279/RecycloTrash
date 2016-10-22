from __future__ import with_statement # Required in 2.5
import signal
from time import sleep
from contextlib import contextmanager

class TimeoutException(Exception): pass

def long_function_call():
    for i in range(10000):
        sleep(1)
        print "hi"

@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException, "Timed out!"
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

#try:
#    with time_limit(10):
#        long_function_call()
#except TimeoutException, msg:
#    print "Timed out!"
