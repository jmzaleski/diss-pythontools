#!/usr/bin/python

# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4 -*-

# reads files left behind from running our modified jamvm under monster
# reads monster .txt session files and extracts the PMC names and totals

from TestEnv       import TestEnv

SFMT="%15s"    #stolen from RunResultReaderVisitor
FFMT="%15.1f"

import re

from DictOfDict import dStrRow, dStrRowOrderedByList, dStrHeaderLine

class PMCResults:
    "describes the totals of the events of a  MONSTER run"

    def __init__(self, n=6) :
        #just init to 8 strings
		self.N_PMC = n # 8 for PPC970, 6 for PPC7450
        self.pmcnames = []
        self.shortPmcnames = []
        for i in range(1,self.N_PMC+2,1) :
            self.pmcnames.append("")
            self.shortPmcnames.append("")
        self.dict = {}

	def toPMCDescriptionString(self) :
        s = ""
		for nam in self.pmcnames :
			s += nam
			s += "\n"
		return s
		
	def toString(self, prefix, rowTitle) :
        s = prefix
        s += dStrHeaderLine(self.shortPmcnames)
        s += dStrRowOrderedByList(self.dict, self.shortPmcnames, rowTitle)
        return s
		
    def __str__(self) :
		return self.toPMCDescriptionString() + self.toString("PMCs")
                             
    def read(self, aFile, legend) :
        """read the file until you find a line matching legend:$.
        The line contains the total of all the monster events for the session ="""

        l = aFile.readline().rstrip("\n")
        if not re.match("Processor 1:",l) :
            raise "first line must start with  Processor 1: instead of " + l + "\nis " + aFile + " a monster file?\n"

        timeBase = aFile.readline().rstrip("\n")

        self.pmcnames[0] = timeBase
        self.shortPmcnames[0] = timeBase[0:15]
            
        for i in range(1,self.N_PMC+1,1) :
            l = aFile.readline().rstrip("\n")
            m = re.search("\(.*\) PMC\s+([1-8]):", l)
            if m :
                ix = int( m.group(1) )
                longName = l.split(":")[1]
                self.pmcnames[ix] =  longName
                self.shortPmcnames[ix] = longName[0:15]

#        print "pmcnames=", self.pmcnames
#        print "shortPmcnames=", self.shortPmcnames
        
#        totalRegexp = re.compile(";" + legend + ":")
        totalRegexp = re.compile( legend + ":")

        # look through the file for lines matching totalRegexp
        # and associate the PMC name string with the datum
        # (I bet this is misguided, should use some short name)
        
        for l in aFile :
            if  totalRegexp.search(l) :
                dict = {}
                ix=int(0)
                for ds in l.split(";")[1:self.N_PMC+2] :
                    self.dict[ self.shortPmcnames[ix] ] = float(ds)
                    ix += 1
#		print 'dict=', self.dict




def readOne(dirName, aTestSuite, aVisitor) :
	"read the data for the benchmark tuns for a vm"
	reader = RunResultReader(TestEnv(None, dirName, None))
	reader.acceptVisitor(aTestSuite, aVisitor)











	
	
from Specjvm98TestSuite import Specjvm98TestSuite

if __name__ == "__main__" :
    me = PMCResults()
    me.read(
        file("jam-distro/scimark_20060519070432.txt","r"),
        "total"
        )
#    print me.dict
#    print dStrRow(me.dict, "PMCs")
    print me

 
#     renderBarchart("complete",
#                    barchart(
#                             "percent completion of average trace",
#                             "%",
#                             "%complete",
#                             d2,
#                             ["%complete"]
#                             )
#                    );
#     renderBarchart("instPerTrace",
#                    barchart(
#                             "instructions dispatched per trace",
#                             "number of virtual instructions",
#                             "instr/tr",
#                             d2,
#                             ["instr/tr"]
#                             )
#                    );

    
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
