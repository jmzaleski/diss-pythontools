# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4 -*-

from Specjvm98TestSuite import Specjvm98TestSuite

class QuickSpecJvm98TestSuite(Specjvm98TestSuite):
    "describes the specjvm98 bucket with low reps so it's quick"
    REPS=1  #change the REPS is all we need to do to make it "quick"









if __name__ == "__main__" :
    from TestEnv import TestEnv
    from JavaVM import JamVM
    vm = JamVM("/home/matz/jwrk/jamvm")
    te = TestEnv(vm, "/tmp", "/tmp")
    me = QuickSpecJvm98TestSuite()
    print me
    me.run(te)

    


    
        
