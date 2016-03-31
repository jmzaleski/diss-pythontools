# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4 -*-

import os

CPCMDLINEOPTION = "-classpath"

class JavaVM:
    "describes a Java VM. subclasses for Sable, Jam, etc"

    def __init__(self, vmAout, cpCmdLineOption = CPCMDLINEOPTION):
        self.vmAout = vmAout  #the interpreter a.out
        self.cpCmdLineOption = cpCmdLineOption
        self.vmDebugOptionString = ""

    def command(self, aTestCase, aTestEnv):
        return "%s %s %s %s %s %s" % ( self.vmAout,
                                      self.vmDebugOptionString,
                                      self.cpCmdLineOption ,
                                      aTestCase.classPath ,
                                      aTestCase.className ,
                                      aTestCase.vmArgs
                                      )
            
#        return self.vmAout + self.cpCmdLineOption + aTestCase.classPath + aTestCase.className + aTestCase.vmArgs

        
        "returns a string that is the command to run the vm"
        

class SableVM ( JavaVM ):
    def __init__(self, vmAout):
        JavaVM.__init__(self, vmAout, "-c")



class JamVM ( JavaVM ):
    def __init__(self, vmAout):
        JavaVM.__init__(self, vmAout)


if __name__ == "__main__":
    print SableVM("/usr/local/bin/sablevm")
    print JamVM("/usr/local/bin/sablevm")



