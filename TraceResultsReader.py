# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4 -*-

# from RunResultReader import RunResultReader
# from RunResultReaderVisitor import MeanRunResultReaderVisitor

from JavaCmdRunner import JavaCmdRunner
from TestEnv       import TestEnv

SFMT="%15s"    #stolen from RunResultReaderVisitor
FFMT="%15.1f"

import re

from DictOfDict import dStrOrderedByList
from DictOfDict import transpose
from DictOfDict import barchart
from DictOfDict import renderBarchart

# m = re.search( '(?P<TYPE>real|user|sys)\D+(?P<TIME>\d+.\d+)', line ) 
# if m : d[m.group('TYPE')]=m.group('TIME');

def readRun(aDirName, aTestSuite, rep, legend) :
    """from a directory called aDirName read the output files from aTestSuite
    read the rep'th file"""

    dict = {}
    
    for aTestCase in aTestSuite.testList :
        sn = aTestCase.shortName
        fn = aDirName + "/" + sn + "-" + rep + "." + JavaCmdRunner.STDOUT_EXT
        f = file( fn, "r")
		if not f:
			raise "cannot open " +  fn
        dict[sn] = read( f, legend );
        f.close()
    return dict
        
def read(aFile, legend) :
		"""read the file until you find a line matching ^legend.
        Then return the number following the ="""
        
		l = aFile.readline().rstrip("\n")
        if not re.match("^MATZ_INSTRUMENT",l) :
 			raise "first line must be CONTEXT rather than" + l

        regexp = re.compile("^" + legend)

        for l in aFile :
            if regexp.match(l) :
                # i've been inconsistent. sometimes blah = 42
                m = re.search('\s+(?P<NUM>[0-9.]+\s)',l)
                if not m :
                    # other times blah=42
                    m = re.search('=(?P<NUM>[0-9.]+)',l)
                    
                if m :
#                   print "group NUM=", m.group('NUM')
                    n = m.group('NUM')
                    return float(n)
                else :
                    raise "didn't find number in " + l
        return 0
        #raise "didn't find " + legend


def readOne(dirName, aTestSuite, aVisitor) :
	"read the data for the benchmark tuns for a vm"
	reader = RunResultReader(TestEnv(None, dirName, None))
	reader.acceptVisitor(aTestSuite, aVisitor)
	
            

# #       print "testShortName=", testShortName, "col1=", col1, "col2=", col2
# #        print testShortName, "x1=", x1, "x2=", x2, "deltap[" + testShortName + "]=", deltap[testShortName]["%"]

# #     print SFMT % "vm", SFMT % col1, SFMT % col2, SFMT % "%"
# #     for testShortName in names :
# #         print SFMT % testShortName, FFMT % deltap[testShortName][col1], FFMT % deltap[testShortName][col2], FFMT % deltap[testShortName]["%"]
		


from Specjvm98TestSuite import Specjvm98TestSuite

# static  traces: created 49 containing 286 blocks 1013 instructions
# static  traces: % of  instrLoaded    = 4.1 %
# dynamic traces: dispatched            =       5214  (about 5.2e+03)
# dynamic traces: completed             =       2612  (about 2.6e+03)
# dynamic traces: exited                =       2463  (about 2.5e+03)
# dynamic traces: instructions executed = 88344 (about 8.8e+04)
# dynamic traces: instr/tr dispatched   = 16.9
# dynamic traces: % complete (hypothl) = 67.0 %

if __name__ == "__main__" :
    dir = "/tmp/virtual"
    dict = {}
    ts = Specjvm98TestSuite()

    dict["dispatched"] = readRun(dir, ts, "0", "dynamic traces: dispatched")
    dict["completed"]  = readRun(dir, ts, "0", "dynamic traces: completed")
    dict["exited"]     = readRun(dir, ts, "0", "dynamic traces: exited")
    dict["instrExec"]  = readRun(dir, ts, "0", "dynamic traces: instructions executed")
    dict["instr/tr"]   = readRun(dir, ts, "0", "^dynamic traces: instr/tr dispatched")
    dict["%complete"]  = readRun(dir, ts, "0", "^dynamic traces: % complete")

    cols = [ "dispatched",  "completed", "exited", "instrExec", "instr/tr", "%complete"]

    d2 = transpose(dict)
    
#    print dStrOrderedByList(d2, ts.shortNames(), cols )
    print dStrOrderedByList(d2, ts.shortNames(), cols )

    renderBarchart("complete",
                   barchart(
                            "percent completion of average trace",
                            "%",
                            "%complete",
                            d2,
                            ["%complete"]
                            )
                   );
    renderBarchart("instPerTrace",
                   barchart(
                            "instructions dispatched per trace",
                            "number of virtual instructions",
                            "instr/tr",
                            d2,
                            ["instr/tr"]
                            )
                   );

    
#     for i in cols :
#         s = barchart(i,i,i,d2, [i] )
#         renderBarchart(i, s)
        
#    s = barchart("dispatched",d2, ["dispatched"] )

#     barFile = open("xx" + ".bar",'w')
#     barFile.write(s)
#     barFile.close()

#     os.system("bargraph %s -o %s" % ( fn + ".bar", fn + ".ps" ) )
#     os.system("ls -l " + fn + "*")
#     os.system("gv " + fn + ".ps")
    



#    read("/tmp/virtual/hello-0.stdout")

# 	from Specjvm98TestSuite import  Specjvm98TestSuite
# 	tab = (
# 		("jam-pure", "/Users/matz/ct/data/jamvm/PPC7410/pure", Specjvm98TestSuite() ),
# 		("sablevm-in","/Users/matz/ct/data/sablevm/PPC7410.python/inline", Specjvm98TestSuite() ),
# 		)
# 	from TestEnv  import TestEnv

# 	d2 = read(tab)
#     l2 = readShortNameList(tab)
    
# 	print dStr( d2 )
# 	print dStr( transpose(d2) )
# 	s = barchart( transpose(d2), "sablevm-in", l2 )
# 	print s
# 	barFile = open("/tmp/xx.bar",'w')
# 	barFile.write(s)
# 	barFile.close()
# 	import os
# 	os.system("bargraph %s -o %s" % ( "/tmp/xx.bar", "/tmp/xx.ps" ) )
# 	os.system("gv /tmp/xx.ps")
