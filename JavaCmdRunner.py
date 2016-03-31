# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4 -*-

from  CmdRunner import  CmdRunner
import os

def run(aTestEnv, aTestCase):
    return JavaCmdRunner(aTestEnv, aTestCase, 0).run()


class JavaCmdRunner(CmdRunner):
  "run a java program"

  STDOUT_EXT="stdout"
  STDERR_EXT="timep"

  def __init__(self, aTestEnv, aTestCase, rep):
    aDict = {}
    aDict["interpCmd"] = aTestEnv.vm.command(aTestCase, aTestEnv)
    aDict["stderrFile"] = "%s/%s-%d.%s" % (aTestEnv.outputDir, aTestCase.shortName,rep, self.STDERR_EXT)
    aDict["stdoutFile"] = "%s/%s-%d.%s" % (aTestEnv.outputDir, aTestCase.shortName,rep,self.STDOUT_EXT)
    aDict["dir"] = aTestCase.dir
    CmdRunner.__init__(self, aDict)


if __name__ == "__main__" :
    import TestCase
    import TestSuite
    from JavaVM import JamVM
    from TestEnv import TestEnv
    print "instatiate JavaCmdrunner"
    tc = TestCase.TestCase("ShortName","", "./classes", "Hello", "/home/matz/ct/javaBench/hello", "")
    vm  =JamVM("/home/matz/jwrk/jamvm")
    te = TestEnv(vm, "/tmp", "/tmp")
    me = JavaCmdRunner(te,tc,42)
    print "about to run cmd ", me.getCmd()
    rs = me.run()
    print rs
