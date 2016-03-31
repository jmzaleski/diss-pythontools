# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4 -*-

# read a bunch of pickled run results and return a list

import glob
import RunResult

# must import TestSuite from TestSuite. otherwise unpickling is foobar.
# i.e. doesn't work to say: import TestSuite

from TestSuite import TestSuite
from TestEnv   import TestEnv
from RunResult import pfn

import os

        
class RunResultReader:
    "reads pickled RunResult instances from a previous bucket run"

    PATTERN = "*" + RunResult.FILEEXT
    
    def __init__(self, aTestEnv):
        self.testEnv = aTestEnv

    def pattern(self):
        return self.testEnv.outputDir + "/" + self.PATTERN 

    def readFiles(self):
        "read data files with names matching pattern"
        list = []
        for fn in glob.glob(self.pattern()):
            rr = RunResult.read(fn)
#            print '====================='
#            print rr
            list.append( rr )
        return list


    def readFilesTestSuite(self, aTestSuite):
        """read data files that SHOULD have been written by aTestSuite
        returns list of RunResult instances"""
        self.checksanity(aTestSuite)
        list = []
        for aTestCase in aTestSuite.testList:
            fn = pfn(self.testEnv, aTestCase)
            aRunResult = RunResult.read(fn)  ### real work ###
            for rs in aRunResult.aListOfRunStatus:
                if not rs.success() :
                    print "failed: ", self.testEnv.outputDir,aTestCase.shortName, rs
            list.append(aRunResult)
#            print aRunResult
        return list
            
    def checksanity(self, aTestSuite):
        "check sanity by making sure all result (pickle) files exist"
        for aTestCase in aTestSuite.testList:
            fn = pfn(self.testEnv, aTestCase)
            if not os.access(fn, os.R_OK):
                raise "sanity: " + fn + " does not exist"
        
        
    def acceptVisitor(self, aTestSuite,aVisitor):
        "run a visitor around the data"
        aVisitor.newTestSuite(self)
        for aRunResult in self.readFilesTestSuite(aTestSuite):
            aVisitor.newTestCase(aRunResult)
            for aResultStatus in aRunResult.aListOfRunStatus:
                if aResultStatus.success() :
                    aVisitor.visit(aResultStatus)
                else :
                    print "*** WARNING\n"
                    print "FAILED:\n" + aRunResult.env.outputDir + " " + aRunResult.testCase.shortName + "\n" + str(aResultStatus)
                    print "****WARNING\n"
            aVisitor.endTestCase()
        aVisitor.endTestSuite()

            
if __name__ == "__main__" :
    from JavaVM import JamVM
    vm = JamVM("/home/matz/jwrk/jamvm")
    te = TestEnv(vm, "/home/matz/ct/data/jamvm/PPC7410/pure", "/tmp/testtmp")
    te.checkSanity()
    me = RunResultReader(te)
    from Specjvm98TestSuite import  Specjvm98TestSuite

    print me.readFilesTestSuite(Specjvm98TestSuite())
    print me.readFiles()
