# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4 -*-

from TestSuite import TestSuite
from TestCase  import TestCase

class Specjvm98TestSuite(TestSuite):
    "describes the specjvm98 bucket"

    dir="/home/matz/ct/javaBench/"
    novmargs=''
    cp='./classes'
    noargs=''
    #           short      vm args, classpath, class name                      dirname,        app args
    #ray should have been raytrace
    #scitest should have been scimark
    SPECLIST=[
        TestCase("hello",   novmargs, cp, "Hello",                              dir + 'hello' ,   noargs) ,
        TestCase("jess",    novmargs, cp, "spec.benchmarks._202_jess.Main",     dir + 'jess',     noargs) ,
        TestCase("javac",   novmargs, cp, "spec.benchmarks._213_javac.Main",    dir + 'javac',    noargs) ,
        TestCase("jack",    novmargs, cp, "spec.benchmarks._228_jack.Main",     dir + 'jack',     noargs) ,
        TestCase("mpeg",    novmargs, cp, "spec.benchmarks._222_mpegaudio.Main",dir + 'mpegaudio',noargs) ,
        TestCase("db",      novmargs, cp, "spec.benchmarks._209_db.Main",       dir + 'db',       noargs) ,
        TestCase("scitest", novmargs, '.', "scitest.tester",                    dir + 'scimark',  "-large") ,
        TestCase("compress",novmargs, cp, "spec.benchmarks._201_compress.Main", dir + 'compress', noargs) ,
        TestCase("mtrt",    novmargs, cp, "spec.benchmarks._227_mtrt.Main",     dir + 'mtrt',     noargs) ,
        TestCase("ray",     novmargs, cp, "spec.benchmarks._205_raytrace.Main", dir + 'raytrace', noargs) ,
        ]
    

    def __init__(self):
        "build a test suite for spec jvm 98"
        TestSuite.__init__(self, self.SPECLIST)
 
# 	def __str__(self):
# 		return " ".join( self.testList )
        
        
if __name__ == "__main__" :
    REPS=3
    from TestEnv import TestEnv
    from JavaVM import JamVM
    vm = JamVM("/home/matz/jwrk/jamvm")
    te = TestEnv(vm, "/tmp/test-tools/jamvm/PPC7410", "/tmp/testtmp",REPS)
    me = Specjvm98TestSuite()
    print me
    me.run(te)

    


    
        
