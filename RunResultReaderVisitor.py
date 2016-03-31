# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4 -*-

class RunResultReaderVisitor:
	"base class for visitors of a RunResultReader"

    SFMT="%10s"
    FFMT="%10.1f"

    "does busywork for all ResultReader visitors"
    def __init__(self):
        self.reset()

    def reset(self):
        self.repList = []
        self.dict = {}
        self.currentRunResult = None
        self.currentResultReader = None

    def newTestSuite(self, aResultReader):
        "initialize from scratch"
        self.reset()
        currentResultReader = aResultReader
#        print "newTestSuite for test environment", aResultReader.testEnv

    def endTestSuite(self):
        "do final calculations"
#        print "endTestSuite for test environment", self.currentResultReader

    def newTestCase(self, aRunResult):
        "prepare to visit bunch of new run results"
        self.repList = []
        self.currentRunResult = aRunResult
#        print "newTestCase has new RunResult for test case ", aRunResult.testCase

    def endTestCase(self):
        "finish calculations for repititions of a test case"
#        print "endTestCase for ", self.currentRunResult
        self.dict[self.currentRunResult.testCase.shortName] = self.repList

    def visit(self, aResultStatus):
        "either calculate some partial result or append to repList"
        self.repList.append(aResultStatus)

    def __str__(self) :
        "pretty print (in a table) the data visited"
        s = self.SFMT % "test case"
        i=0
        #run along a random row. They all should be the same.
        for aResultStatus in self.dict[self.dict.keys()[0]]:
            s += self.SFMT % ("REP"+str(i))
            i += 1
        s += "\n"
        for name in  self.dict.keys():
            s += self.SFMT % name
            for aResultStatus in self.dict[name]:
                s += self.FFMT % float(aResultStatus.elapsedTime)
            s += "\n"
        return s


class MeanRunResultReaderVisitor( RunResultReaderVisitor ) :
    "calculate the mean of each set of reps"

    def endTestCase(self) :
        "calculate stuff the mean"
        total = 0.0
        n = 0
        for aResultStatus in self.repList :
            n += 1
            total = total + float( aResultStatus.elapsedTime )
        self.dict[self.currentRunResult.testCase.shortName] = total/float(n)

    def __str__(self) :
        "pretty print (in a table) the data visited"
        s = ""
        s += self.SFMT % "test case"
        s += self.SFMT % "MEAN"
        s += "\n"
        
        for name in  self.dict.keys():
            s += self.SFMT % name
            s += self.FFMT % self.dict[name]
            s += "\n"
        return s


if __name__ == "__main__" :
    from TestSuite import TestSuite
    from TestEnv   import TestEnv
    from JavaVM import JamVM
    from RunResultReader import RunResultReader
    
#    vm = JamVM("/home/matz/jwrk/jamvm")
#    te = TestEnv(vm, "/home/matz/ct/data/jamvm/PPC7410/pure", "/tmp/testtmp")
    te = TestEnv(None, "/home/matz/ct/data/jamvm/PPC7410/pure", None)
#    te.checkSanity()

    me = RunResultReader(te)
    from Specjvm98TestSuite import  Specjvm98TestSuite

    print me.readFilesTestSuite(Specjvm98TestSuite())
    
    aVisitor = RunResultReaderVisitor()
    me.acceptVisitor(Specjvm98TestSuite(), aVisitor)
    print aVisitor

    aVisitor = MeanRunResultReaderVisitor()
    me.acceptVisitor(Specjvm98TestSuite(), aVisitor)
    print aVisitor



        
