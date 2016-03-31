# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4 -*-

from RunResultReader import RunResultReader
from RunResultReaderVisitor import MeanRunResultReaderVisitor
from TestEnv         import TestEnv
SFMT="%15s"    #stolen from RunResultReaderVisitor
FFMT="%15.1f"


def readOne(dirName, aTestSuite, aVisitor) :
	"read the data for the benchmark tuns for a vm"
	reader = RunResultReader(TestEnv(None, dirName, None))
	reader.acceptVisitor(aTestSuite, aVisitor)
	
def read(tab) :
	"""produce a dict-o-dicts keyed by vm short name
    mostly the transpose is useful"""
	dict = {}
	aVisitor = MeanRunResultReaderVisitor()
	for aTuple in tab :
		readOne(aTuple[1], aTuple[2], aVisitor)
		dict[ aTuple[0] ] = aVisitor.dict
	return dict

def readShortNameList(tab) :
    "read same table to extract list ordering VM short names"
    aList = []
	for aTuple in tab :
        aList.append( aTuple[0] )
	return aList
    
def dStr(dict) :
	"""pretty print one of our dict-o-dict 2d matrices
    The obvious issue is which order to visit the rows and
    columns. This method does it more or less randomly,
    Each dimension is visited in order of keys().
    """
	s = SFMT % "VM"
	vmname = dict.keys()[0] #basically a random key from outer dict
	for testShortName in dict[vmname].keys() :
		s += SFMT % testShortName
	s += "\n"
	
	for k1 in dict.keys() :
		s += SFMT % k1
		for k2 in dict[k1].keys() :
			s += FFMT % dict[k1][k2]
		s += "\n"
	return s


def dStrOrderedByList(dict,k1NameList, k2NameList) :
	"""pretty print one of our dict-o-dict 2d matrices.
    print test cases in order given by k1NameList and k2NameList parms"""

    #column headers. order comes from k2NameList
	s = SFMT % "VM"
    for testShortName in k2NameList :
		s += SFMT % testShortName
	s += "\n"
    #now iterate through the dict-o-dicts
	for k1 in k1NameList :
		s += SFMT % k1
		for k2 in k2NameList :
			s += FFMT % dict[k1][k2]
		s += "\n"
	return s

def transpose(dict) :
    "well, if it's a 2d matrix that means I can transpose it, right?"
	tdict = {}
	vmname = dict.keys()[0] #basically a random key from outer dict
	for testShortName in dict[vmname].keys() :
		tdict[testShortName] = {}
	for k1 in dict.keys() :
		for k2 in dict[k1].keys() :
			tdict[k2][k1] = dict[k1][k2]
	return tdict


def deltaPerCent(dict, col2, col1) :
    """calculate the  delta percent difference between two cols of the matrix
    outermost keys of dict are test case names.
    return a dict-o-dict with a three columns. col1, col2, "%".
    """

#    print "dict=", dict
    deltap = {}
    names = dict.keys() # outermost dict keyed by test case names
#    print "names=", names

    for testShortName in names :
        deltap[testShortName] = {}
        deltap[testShortName][col1] = dict[testShortName][col1]
        deltap[testShortName][col2] = dict[testShortName][col2]
        deltap[testShortName]["%"]  = 0.0

    for testShortName in names :
        x1 = dict[testShortName][col1]
        x2 = dict[testShortName][col2]
        if ( x1 != 0.0 and x2 != 0.0 ) :
            deltap[testShortName]["%"] = 100.0 * (x2 - x1) / x1
    return deltap
            

#       print "testShortName=", testShortName, "col1=", col1, "col2=", col2
#        print testShortName, "x1=", x1, "x2=", x2, "deltap[" + testShortName + "]=", deltap[testShortName]["%"]

#     print SFMT % "vm", SFMT % col1, SFMT % col2, SFMT % "%"
#     for testShortName in names :
#         print SFMT % testShortName, FFMT % deltap[testShortName][col1], FFMT % deltap[testShortName][col2], FFMT % deltap[testShortName]["%"]
		
    

# we set the labels to be rotated by -xlabelangle 90.
# this requires us also to set a bottommargin large enough to
# accomodate them (the 1.5 discovered long enough by trial and error)
# Also, we have to move the label down below the cluster lables
# by -labeldist 1.2. The 1.2 inches is just enough to put the X axis
# legend below the cluster labels and in the bottom margin.
# (This value also discovered purely by trial and error)

title = """
Title: %(platform)s Elapsed execution time relative to %(base)s
YAxis: %(platform)s time -p relative to %(base)s
XAxis: Spec JVM98 Benchmarks : -labeldist 1.2
Key:  right, top: Legend :
Options: -xlabel 0.5 -keyfirst -rightmargin 2 -bottommargin 1.5
""";

#create commands intended for bargraph, the uber-perlscript
#that Angela has introduced us to.

#	my ($cf, @benchmarks, $bm, $br, $vm, $btest, $cbase, $ctest,);

#oh oh, need to establish an order for the benchmarks (clusters)
#and VMs within them.

def barchart(platform, d2, base, l2):
	"return string that can be thrown at barchart"
    #vm names are sorted lexically.
    #test case name order comes in from l2.
    tclist = d2.keys()
    tclist.sort()
    s = title % {"base":base, "platform":platform}
    for tc in tclist :
		s += ("BeginCluster: " + tc + " : -xlabelangle 90 \n")
#		for vm in d2[tc].keys() :
        for vm in l2 :
			s += "Bar: %.2f : %s \n" % ( d2[tc][vm]/d2[tc][base], vm )
		s += "EndCluster\n"
	return s


	

if __name__ == "__main__" :
	from Specjvm98TestSuite import  Specjvm98TestSuite
	tab = (
		("jam-pure", "/home/matz/ct/data/jamvm/PPC7410/pure", Specjvm98TestSuite() ),
		("sablevm-in","/home/matz/ct/data/sablevm/PPC7410.python/inline", Specjvm98TestSuite() ),
		)
	from TestEnv  import TestEnv

	d2 = read(tab)
    l2 = readShortNameList(tab)
    
	print dStr( d2 )
	print dStr( transpose(d2) )
	s = barchart( transpose(d2), "sablevm-in", l2 )
	print s
	barFile = open("/tmp/xx.bar",'w')
	barFile.write(s)
	barFile.close()
	import os
	os.system("bargraph %s -o %s" % ( "/tmp/xx.bar", "/tmp/xx.ps" ) )
	os.system("gv /tmp/xx.ps")
