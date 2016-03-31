# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4 -*-

import os

class TestCase:
  """describe the data specific to a (Java?) test case. 
      In conjunction with a TestSuite and TestEnv can be executed"""

  def __init__(self, shortName, vmArgs, cp, cl, dir, clargs=''):
      self.shortName = shortName
      self.vmArgs = shortName
      self.vmArgs = vmArgs
      self.classPath = cp
      self.className = cl
      self.dir = dir
      self.vmArgs = clargs

  def __str__(self):
      return "%s vmArgs=%s classPath=%s className=%s dir=%s vmArgs=%s" % (
          object.__str__(self), self.vmArgs, self.classPath, self.className, self.dir, self.vmArgs
          )

  def checkSanity(self):
    if not os.path.exists(self.dir): raise "sanity: no path " + self.dir
    coreFile = self.dir + "/core"
    if os.path.isfile( coreFile): raise "sanity: corefile exists:" + coreFile

    
if __name__ == "__main__" :
    print "instatiate TestCase"
    me = TestCase("MyShortName", "-vmargs", ".", "Hello", "/home/matz/ct/javaBench/hello", "")
    print me
