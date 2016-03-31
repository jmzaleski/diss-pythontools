# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4 -*-

import os
import signal
import re

class RunStatus:
   def __init__(self, didExit, errorMsg='', exitCode=0, realTime=0.0, userTime=0.0, sysTime=0.0):
       self.didExit     = didExit             #did program run to completion or signal
       self.exitCode    = exitCode            #oh oh either signal of other badness
       self.elapsedTime = realTime            #from /usr/bin/time, or whatever
       self.userTime    = userTime
       self.sysTime     = sysTime
       self.errorMsg    = errorMsg

   def threw(self):
      return not self.didExit
   
   def success(self):
      return self.didExit and (self.exitCode == 0)

   def __str__(self):
      if self.threw():
         return "%s Fail. could not run or threw signal %s" % (self.errorMsg, self.exitCode)
      if not self.success():
         return "%s Fail exit status %s" % (self.errorMsg, self.exitCode)
      if self.success():
         return "%s cpu time: real=%s user=%s sys=%s" % (self.errorMsg, self.elapsedTime, self.userTime, self.sysTime)


class CmdRunner:
   PROP = {
#        "perfWrapper":"/usr/bin/time -p" ,
       "perfWrapper":"time -p" ,
        "interpCmd":"/bin/pwd",
        "stderrFile":"/tmp/stderrFile",
        "stdoutFile":"/tmp/stdoutFile",
        "dir":"/tmp"
        }

   def __init__(self, aDict=None):
     self.dict_ = self.PROP
     if aDict != None :
         for k in aDict.keys():
             self.dict_[k] = aDict[k]

   def interp(self, aString):
      return aString % self.dict_
   
   def getCmd(self):
       #note we run interpCmd in a subshell so we can redirect output of built time to stderrFile
       return self.interp("( %(perfWrapper)s %(interpCmd)s ) 2> %(stderrFile)s  1> %(stdoutFile)s")

   def stderrFile(self):
       return self.interp("%(stderrFile)s")

   def stdoutFile(self):
       return self.interp("%(stdoutFile)s")



   def run(self):
    "run the test case, finally"
    dir = self.dict_["dir"]

    try:
       os.chdir(dir)
    except OSError:
       print 
       return RunStatus(False,"failed to cd to %s" % dir);
       
#    print os.getcwd()

    coreFile = os.getcwd() + "/core"

#     if os.path.isfile( coreFile):
#         raise "Shouldn't happen: corefile exists:" + coreFile
    
    cmd = self.getCmd()
    print 'about to run command ', cmd

    rc = os.system(cmd) ######## REAL WORK ################

#     if os.path.isfile( coreFile):
#         os.rename(coreFile, coreFile + pid #how to find out pid of child??

    if os.WIFEXITED(rc):
       exitrc = os.WEXITSTATUS(rc)

       if exitrc == 255:
           raise "WIFEXITED 255. Assuming this result of matz hack to jamvm thead.c for SIGINT. outa here"
           
       if exitrc == 0:
           print 'exited with code 0 -- sucess'
           d = {}
           for line in open(self.interp("%(stderrFile)s"),'r').readlines():
              m = re.search( '(?P<TYPE>real|user|sys)\D+(?P<TIME>\d+.\d+)', line ) 
              if m : d[m.group('TYPE')]=m.group('TIME');
           return RunStatus(True, "success", 0, d["real"], d["user"], d["sys"])
       else:
           print 'exited with failing code ', exitrc
           return RunStatus(True, "exited failing code", exitrc)
    else:
        exitrcsig = os.WTERMSIG(rc)
        print "terminated with signal", exitrcsig
        if exitrcsig == signal.SIGINT:
           raise "benchmark ended with SIGINT. Assume you want to quit, eh"
        return RunStatus(False, "threw", exitrcsig)



           
if __name__ == "__main__" :
    print "instatiate Cmdrunner"
    me = CmdRunner({"stdoutFile":"xx"})
    me.dict_["stderrFile"] = "/tmp/timep"
    print "me=", me
    print "cmd to run", me.getCmd()
    rs = me.run()
    print rs;
    if ( rs.success() ):
       print "worked"
       
    os.system( me.interp("cat %(stderrFile)s") )


    
