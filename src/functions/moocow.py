import atexit
import inspect
import sys
from timeit import default_timer as timer


class LineTime(object):

    tm = []

    def __init__(self, exitreport=False, deltareport=False):
        self.delta_report = deltareport
        self.exit_report = exitreport
        if deltareport:
            atexit.register(self.deltas)
        if exitreport:
            self.tm.append((0, timer()))
            atexit.register(self.exit)
        pass

    def add(self, offset=0):
        fr = inspect.currentframe()
        for depth in range(offset,1):
            fr = fr.f_back
        lineno = fr.f_lineno
        self.tm.append((lineno, timer()))

    def deltas(self):
        if not self.delta_report:
            return
        last = None
        self.tm = [ t for t in self.tm if t[0] < 99999999 ]
        mxlen = str(len(str(self.tm[-1][0])))
        fmt = "{:>" + mxlen + "} -> {:>" + mxlen + "} {:>.4f}"
        for add in self.tm:
            if last is None:
                last = add
                continue
            d = add[1] - last[1]
            print fmt.format(last[0], add[0], d)
            last = add

    def set_reports(self, **kwargs):
        self.exit_report = kwargs['exitreport']
        self.delta_report = kwargs['deltareport']

    def exit(self):
        if not self.exit_report:
            return
        self.tm.append((99999999, timer()))
        t = self.tm
        elapsed = t[-1][1] - t[0][1]
        (frame, filename, line_number, function_name, lines,
         index) = inspect.getouterframes(inspect.currentframe())[0]
        print "%s exiting. Total elapsed: %s" % (filename, elapsed)
#        print "%s exiting. Total elapsed: %s" % (sys.argv[0], elapsed)



def tst():
    time.sleep(3)
    lt.add()

if __name__ == "__main__":
    import time

    lt = LineTime(deltareport=True, exitreport=True)
    lt.add()
    time.sleep(1)
    lt.add()
    time.sleep(2)
    lt.add()
    tst()