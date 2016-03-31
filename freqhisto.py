# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4 -*-

import math

class BasicBlockDescriptor:
	"struct like t_block_descriptor"

	def __init__(self):
		self.count = 0
		self.dups=0
		self.instrCount=0
		self.codeLen=0

	def __str__(self) :
		return "bb dups=" + str(self.dups) + " instrCount=" + str(self.instrCount) + " count=" + str(self.count)


class BbReader:
	"reads data from bb file"

	def __init__(self, aFilename):
		self.filename = aFilename
        self.list = []

    #
    # put bb's into n bins by log frequency of execution?
    #
    def bin(self,n) :
        freq = []
        for i in range(n) :
            freq.append(0)
        min=10000000000
        max=0
        for bb in self.list :
            if bb.count < min :
                min = bb.count
            if bb.count > max :
                max = bb.count
        #print "max=", max, "min=", min
        logrange= math.log(max-min,10)
        binwidth = logrange/(n);  # on log scale
        for bb in self.list :
            if bb.count == 0 :
                ibin = 0
            else :
                ibin = int( math.log(bb.count-min,10)/binwidth )
                if ibin > (n-1) :
                    ibin = n - 1
                freq[ibin] = freq[ibin] + 1
        return freq

    
	def read(self) :
		"read the file a produce a bunch of bb. append to instance list"
		f = file( self.filename, "r")
		if not f:
			raise "cannot open " +  self.filename

		l = f.readline().rstrip("\n")
		if not l == "<bblist>" :
			raise "first line must be <bblist> rather than" + l

		while True :
			l = f.readline().rstrip("\n")
			if l == "</bblist>" :
				break
			words = l.split()
			bb = BasicBlockDescriptor()
			bb.dups       = int(words[0])
			bb.instrCount = int(words[1])
			bb.count      = int(words[2])
			self.list.append(bb)




title = """
Title: %(platform)s log freq histogram
YAxis: %(platform)s number of linear regions in execution freq bin
XAxis: bb's (bin by freq of execution)
Key:  right, top: Legend :
Options: -xlabel 0.5 -keyfirst -rightmargin 2 -bottommargin 1.5
""";

def barchart(platform, freq):
	"return string that can be thrown at barchart"

    s = title % {"platform":platform}
    i = 0
    for bin in freq :
		s += ("BeginCluster: " + str(i) + ":\n")
        s += "Bar: %.2f : %s \n" % ( freq[i], str(i) )
		s += "EndCluster\n"
        i = i + 1
	return s

    

def renderBarchart(fn) :
    fnbar = fn  + ".bar"
    fnps = fn  + ".ps"
    print fn, fnbar, fnps
    
	bbr = BbReader(fn)
    bbr.read()
    bbr.sortfreq()
    freq = bbr.bin(100)
    s = barchart("aplatform",freq)
	barFile = open( fnbar, 'w')
	barFile.write(s)
	barFile.close()
	import os
	os.system("bargraph %s -o %s" % ( fnbar, fnps ) )
#	os.system("gv " + fnps )

    
def freqGraph(x0, aListOfBb, func) :
    "return a string that can be thrown at gnu graph for a log freq vs bb graph"
    s = ""
    i = x0
    #log scale doesn't like zero, so turn it into 1 which will display zero as zero
    #but we want to distinguish freq 0 and freq 1. so fudge 1 to 1.5
    for bb in aListOfBb :
        s += str(i)
        s += " "
        y = func(bb)
        if y < 0 : raise "hey, how come freq data < 0"
        if y == 0 :
            y = 1
        s += str(y)   
        s += "\n"
        i += 1
    return s


def renderFreqGraph(fn) :
    "use gnu plotutils graph to render a graph of bb vs frequency of execution"
    stem = fn[0:fn.rindex(".dat")]  #strip off the .dat.
    fngraph0 = stem  + "-freq-0.graph"
    fngraph = stem  + "-freq.graph"
    fnps = stem  + "-freq.ps"
    print fn, stem, fngraph, fnps
    
	bbr = BbReader(fn)
    bbr.read()

    bbr.list.sort(lambda bb1,bb2: cmp(bb1.count, bb2.count) )

    # idea here is to plot the bb's that execute zero times in a different color
    list0 = [bb for bb in bbr.list if bb.count == 0]
    s0 = freqGraph(0,list0, lambda bb: bb.count)
	gFile = open( fngraph0, 'w');	gFile.write(s0); gFile.close()

    list = [bb for bb in bbr.list if bb.count > 0]
    s = freqGraph(len(list0),list, lambda bb: bb.count)
	gFile = open( fngraph, 'w');	gFile.write(s); gFile.close()
    
	import os
    graphOptions = " -Tps "
    graphOptions += " --top-label " + stem
    graphOptions += ' --x-label \"linear region (sorted by frequency)\" '
    graphOptions += ' --y-label \"frequence of dispatch (log)\" '
    graphOptions += " --toggle-log-axis y "
    graphOptions += " --line-mode 0 "
    graphOptions += " --symbol 1 0.09 "
	print "graph %s %s > %s" % ( graphOptions, fngraph, fnps ) 

	os.system("graph %s -C %s -C %s > %s" % ( graphOptions, fngraph0, fngraph, fnps ) )
#	os.system("gv " + fnps )
    
import sys

if __name__ == "__main__" :
    fn = sys.argv[1]
    renderFreqGraph(fn)
#    renderBarchart(fn)
    
