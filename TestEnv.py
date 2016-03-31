# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4 -*-

import os

class TestEnv:
    """describes the stuff needed to run a TestSuite that is common to all the test cases, 
    for instance the vm executable to run and where to write the temp files and output files"""

    def __init__(self, aVm, outputDir, tmpDir="/tmp/test",repititions=1):
        self.vm = aVm  #an instance describing the VM
        self.outputDir = outputDir
        self.repititions = repititions
        
    def checkSanity(self):
        "make sure the directories exist"
        if not  os.access(self.outputDir,os.W_OK): raise "sanity: no output dir: " + self.outputDir
        if not os.access(self.vm.vmAout, os.X_OK): raise "sanity: no vm: " + self.vm.vmAout


