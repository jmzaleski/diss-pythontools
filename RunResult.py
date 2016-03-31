# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4 -*-

import pickle

FILEEXT=".pickle"


def read(fn):
    """read from a pickled file written during a data collection run
    return a RunResult instance"""
    fp = open( fn, "r")
    if not fp:
        raise "oh oh failed to open", fn, " for read"

    try:
        obj = pickle.load(fp)
    except:
        fp.close
        raise "failed to read pickle file " + fn
    return obj

#this should move to a new class called ResultWriter

def pfn(aTestEnv, aTestCase):
    return aTestEnv.outputDir + "/" + aTestCase.shortName + FILEEXT
    

class RunResult :
    "maintains the results of running a benchmark a number of times"
    def __init__(self, aListOfRunStatus, aTestEnv, aTestCase):
        self.aListOfRunStatus   = aListOfRunStatus
        self.env      = aTestEnv
        self.testCase = aTestCase

    def __str__(self):
        s =  object.__str__(self) + "\n  " +  str(self.env) + "\n  " + str(self.testCase) + "\n  " + ( "list of %d RunStatus instances:" % len(self.aListOfRunStatus ) )
        for rs in self.aListOfRunStatus:
            s = s + "\n  " + str(rs)
        return s

    def pickleFilename(self):
        return pfn(self.env, self.testCase)

#        return self.env.outputDir + "/" + self.testCase.className + FILEEXT

    def write(self):
        fp = open( self.pickleFilename(), "w")
        pickler = pickle.Pickler(fp)
        pickler.dump(self)
        fp.close


if __name__ == "__main__":
    from  TestSuite  import TestSuite
    from  TestEnv    import TestEnv
    from  TestCase   import TestCase
    import CmdRunner
    from JavaVM import JamVM
    vm = JamVM("/home/matz/jwrk/jamvm")
    te = TestEnv(vm, ".", ".")
    rs = CmdRunner.RunStatus(True, "successness", 0, 1.0, 1.0, 1.0)
    tc = TestCase("shortname","", "./classes", "Hello", "/home/matz/ct/javaBench/hello", "")
    me = RunResult([rs],te,tc)
    print me
    me.write()

    print "have written RunResult to ", me.pickleFilename(), " and now will try to read it back"
    print read(me.pickleFilename())

    

        
