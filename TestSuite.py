# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4 -*-

from JavaCmdRunner import JavaCmdRunner

from RunResult import RunResult
from RunResult import read         #probably slicker way to do this
from RunResult import pfn          #probably slicker way to do this

import os
import sys
        
class TestSuite:
    "describes a bunch of tests and the data common to all of them required to run the suite"
    ""
    def __init__(self, aList):
        "build a test suite from a list of TestCase instances"
        self.testList = aList

    def skip(self, aShortNameToSkip) :
        "remove a test case from a suite, presumably because it is busted temporarily"
        i = 0
        for aTestCase in self.testList :
            if aTestCase.shortName == aShortNameToSkip :
                del self.testList[i]
                return self
            i += 1
        raise "skip failed to find test case with short name " + aShortNameToSkip

    def runOnly(self, aShortNameToRun) :
        "remove all test cases from a suite except for the parm"
        newList = []
        for aTestCase in self.testList :
            if aTestCase.shortName == aShortNameToRun :
                newList = [ aTestCase ]
        self.testList = newList

    def __str__(self):
        return object.__str__(self) + " runs: " +  ' '.join([str(i) for i in self.testList] )

    #factory method to be overridden
    def newCmdRunner(self, aTestEnv, aTestCase, rep):
        return JavaCmdRunner(aTestEnv, aTestCase, rep)

    def runOne(self, aTestCase, aTestEnv, rep):
        "execute one test case in the suite and return the ReturnResult"
        #cr = JavaCmdRunner(aTestEnv, aTestCase, rep)
        cr = self.newCmdRunner(aTestEnv, aTestCase, rep)
        rs = cr.run()
        self.verbose(cr)
        return rs

    def verbose(self, cr):
        print '<<stderr>>'
        os.system("head -3 " + cr.stderrFile())
        print '<<stdout>>'
        os.system("head -3 " + cr.stdoutFile())
#        os.system("ls -l " + rr.pickleFilename() )

    def runReps(self, aTestCase, aTestEnv):
        resultList = []
        failed = 0
        for rep in range(aTestEnv.repititions):
            print '=== about to run rep %d ' % rep
            rs = self.runOne(aTestCase, aTestEnv, rep) ####### real work ######
            resultList.append(rs)
            if not rs.success():
                failed = failed + 1
        rr = RunResult(resultList, aTestEnv, aTestCase)                
        rr.write() #pickle it
        rrrr = read(rr.pickleFilename()) #and make sure it's readable. move this call
#        self.verbose(cr,rr)
        return failed

    def run(self, aTestEnv):
        aTestEnv.checkSanity()
        self.checkNoClobber(aTestEnv) ##might not always want this..
        self.checkSanity()
        failed = 0
        i = 0
        n = len(self.testList)
        for aTestCase in self.testList:
            print '----------- about to run %s (%d of %d) -------------' % (aTestCase.className, i, n)
            f = self.runReps(aTestCase, aTestEnv)  ######## real work #########
            failed = failed + f
            i = i + 1
            print "////////// %d failed so far /////////" % failed

    def checkSanity(self):
        for aTestCase in self.testList:
            aTestCase.checkSanity()
        for aTestCase in self.testList:
            datFileName = self.dir + aTestCase.shortName + "/" + aTestCase.className + ".dat"
            print "check for .dat file", datFileName
            if os.path.isfile(datFileName): raise ".dat file exists: " + datFileName

	def checkNoClobber(self, aTestEnv):
		"make sure no data files will be clobbered"
        for aTestCase in self.testList:
            fn = pfn(aTestEnv, aTestCase)
            if os.path.exists(fn):
                raise "output data file: " + fn + " already exists"
            
    def shortNames(self) :
        sn = []
        for aTestCase in self.testList :
            sn.append(aTestCase.shortName)
        return sn

        
if __name__ == "__main__" :
    from TestEnv  import TestEnv
    from TestCase import TestCase
    from JavaVM import JamVM
    
    l = [ TestCase("shortname","", "./classes", "Hello", "/home/matz/ct/javaBench/hello", "") ,
          ]
    vm  =JamVM("/home/matz/jwrk/jamvm")
    te = TestEnv(vm,"/tmp/test-tools/jamvm", "/tmp/testtmp")
    te.checkSanity()
    
    me = TestSuite(l,3)
    print me
    me.run(te)
    
#    print object.__str__(me) + "runs:\n" +  '\n'.join( [i.__str__() for i in me.testList] )
#    me.run(te)
#    rs = me.runOne(hello,te)
#    print rs
    


    
        
