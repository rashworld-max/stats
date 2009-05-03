import sys
import time

def log(s):
    print >>sys.stderr, s,
    sys.stderr.flush()
    return

def tries(ntries, fn, *arglist, **argdict):
    """
    Borrowed from Asheesh.
    """
    tried = 0
    while True:
        try:
            return fn(*arglist, **argdict)
        except Exception, e:
            if isinstance(e, KeyboardInterrupt):
               raise e
            log("Huh, while calling %s, %s happened." % (fn, e))
            tried += 1
            if tried >= ntries:
                raise
            sleeptime = 2 ** tried * 5
            log('trying again after sleeping for %d' % sleeptime)
            time.sleep(sleeptime)

