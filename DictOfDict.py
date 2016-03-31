# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4 -*-

SFMT="%15s"    #stolen from RunResultReaderVisitor
FFMT="%15.1f"

#just a few service routines to help deal with my cheesy
#2d array implemented as a dictionary of dictionaries

def stringFormat(self):
    return SFMT;

def floatForat(self):
    return FFMT;

def dStrRowOrderedByList(dict, list, rowTitle) :
    "pretty print a one d dictionary assuming it's like a dict-o-dicts"
    s = SFMT % rowTitle
    for k2 in list :
        s += FFMT % dict[k2]
    s += "\n"
    return s
    
def dStrRow(dict, rowTitle) :
    return dStrRowOrderedByList(dict, dict.keys(), rowTitle)

def dStrHeaderLine(list, header=''):
    "factor out header line creation"
    s = SFMT % header
    for n in list :
        s += SFMT % n
    s += "\n"
    return s
    
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


def dStrCSV(dict) :
    """spit out one of our dict-o-dict 2d matrices as a CSV file
    to make it easy to read into excel.
    """
    s = SFMT % "VM"
    vmname = dict.keys()[0] #basically a random key from outer dict
    for testShortName in dict[vmname].keys() :
        s += SFMT % testShortName
        s += ", "
    s += "\n"

    for k1 in dict.keys() :
        s += SFMT % k1
        for k2 in dict[k1].keys() :
            s += FFMT % dict[k1][k2]
        s += "\n"
    return s


def dStrOrderedByList(dict, k1NameList, k2NameList) :
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


def dStrOrderedByListCSV(dict, k1NameList, k2NameList) :
    """pretty print one of our dict-o-dict 2d matrices.
    print test cases in order given by k1NameList and k2NameList parms"""

    #column headers. order comes from k2NameList
    s = SFMT % "VM"
    s += ", "
    for testShortName in k2NameList :
        s += SFMT % testShortName
        s += ", "
    s += "\n"
    
    #now iterate through the dict-o-dicts
    for k1 in k1NameList :
        s += SFMT % k1
        s += ", "
        for k2 in k2NameList :
            s += FFMT % dict[k1][k2]
            s += ", "
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


# we set the labels to be rotated by -xlabelangle 90.
# this requires us also to set a bottommargin large enough to
# accomodate them (the 1.5 discovered long enough by trial and error)
# Also, we have to move the label down below the cluster lables
# by -labeldist 1.2. The 1.2 inches is just enough to put the X axis
# legend below the cluster labels and in the bottom margin.
# (This value also discovered purely by trial and error)

title = """
Title: %s
YAxis: %s
XAxis: Spec JVM98 Benchmarks : -labeldist 1.2
Key:  right, top: Legend :
Options: -xlabel 0.5 -keyfirst -rightmargin 2 -bottommargin 1.5
""";

#create commands intended for bargraph, the uber-perlscript
#that Angela has introduced us to.

#   my ($cf, @benchmarks, $bm, $br, $vm, $btest, $cbase, $ctest,);

#oh oh, need to establish an order for the benchmarks (clusters)
#and VMs within them.

def barchart(titleCaption, ycaption, unused, dictOdict, clusterList):
    """return string that can be thrown at barchart.
    graphs a dict-o-dicts passed as parm as a barchart
    where the outer set of keys are the Clusters
    and the inner set of keys are drawn as bars within the cluster.
    hence, dictOdict[benchmark..][trial] is the usual thing we want to draw.
    We establish the order of the clusters, usually benchmarks, by sorting lexically.
    The order of the trials within each cluster is established by clusterList.
    Hence, the clusterList list had better contain only keys of the inner dim of dictOdict!
    """
    #test case name order comes from lexical sort of outer keys of dict
    tclist = dictOdict.keys()
    tclist.sort()

    #sanity check that clusterList doesn't contain any strings that aren't keys
    #of the inner dictionary of dictOdict
    randomInner = dictOdict[dictOdict.keys()[0]]
    for i in clusterList :
        if not randomInner.has_key(i) :
            raise "oops, clusterList includes " + i + " but this is not a inner key of the dict-o-dicts"

    s = title % ( titleCaption, ycaption )
    for tc in tclist :
        s += ("BeginCluster: " + tc + " : -xlabelangle 90 \n")
        for clusterEle in clusterList :
            s += "Bar: %.2f : %s \n" % ( dictOdict[tc][clusterEle], clusterEle )
        s += "EndCluster\n"
    return s
    

def barchartRelativeToBase(platform, d2, base, l2):
    "return string that can be thrown at barchart"
    #vm names are sorted lexically.
    #test case name order comes in from l2.
    tclist = d2.keys()
    tclist.sort()
    print tclist
    print l2
    s = title % {"base":base, "platform":platform}
    for tc in tclist :
        s += ("BeginCluster: " + tc + " : -xlabelangle 90 \n")
        for vm in l2 :
            s += "Bar: %.2f : %s \n" % ( d2[tc][vm]/d2[tc][base], vm )
        s += "EndCluster\n"
    return s


def deltaPerCent(dict, col2, col1) :
   """calculate the  delta percent difference between two cols of the matrix
    outermost keys of dict are test case names.
    return a dict-o-dict with a three columns. col1, col2, "%".
    """
   print "dict=", dict
   deltap = {}
   names = dict.keys() # outermost dict keyed by test case names
   print "names=", names

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


    

# # we set the labels to be rotated by -xlabelangle 90.
# # this requires us also to set a bottommargin large enough to
# # accomodate them (the 1.5 discovered long enough by trial and error)
# # Also, we have to move the label down below the cluster lables
# # by -labeldist 1.2. The 1.2 inches is just enough to put the X axis
# # legend below the cluster labels and in the bottom margin.
# # (This value also discovered purely by trial and error)

# title = """
# Title: %(platform)s Elapsed execution time relative to %(base)s
# YAxis: %(platform)s time -p relative to %(base)s
# XAxis: Spec JVM98 Benchmarks : -labeldist 1.2
# Key:  right, top: Legend :
# Options: -xlabel 0.5 -keyfirst -rightmargin 2 -bottommargin 1.5
# """;

# #create commands intended for bargraph, the uber-perlscript
# #that Angela has introduced us to.

# # my ($cf, @benchmarks, $bm, $br, $vm, $btest, $cbase, $ctest,);

# #oh oh, need to establish an order for the benchmarks (clusters)
# #and VMs within them.

# def barchart(platform, d2, base, l2):
#   "return string that can be thrown at barchart"
#     #vm names are sorted lexically.
#     #test case name order comes in from l2.
#     tclist = d2.keys()
#     tclist.sort()
#     s = title % {"base":base, "platform":platform}
#     for tc in tclist :
#       s += ("BeginCluster: " + tc + " : -xlabelangle 90 \n")
# #     for vm in d2[tc].keys() :
#         for vm in l2 :
#           s += "Bar: %.2f : %s \n" % ( d2[tc][vm]/d2[tc][base], vm )
#       s += "EndCluster\n"
#   return s

import os

def renderBarchart(fileNameStem, s, options='') :
    "take a string in bargraph language and render it to postscript"
    print "fileNameStem=",fileNameStem
    barFile = open(fileNameStem + ".bar",'w')
    barFile.write(s)
    barFile.close()
    os.system("bargraph %s %s -o %s" % ( options, fileNameStem + ".bar", fileNameStem + ".ps" ) )
    os.system("ls -l " + fileNameStem + "*")
#    os.system("gv " + fileNameStem + ".ps")


from Specjvm98TestSuite import Specjvm98TestSuite

if __name__ == "__main__" :
    dir = "/tmp/virtual"
    dict = {}
    ts = Specjvm98TestSuite()
    dict["dispatched"] = readRun(dir, ts, "0", "dynamic traces: dispatched")
    dict["completed"] = readRun(dir, ts, "0", "dynamic traces: completed")
    dict["exited"] = readRun(dir, ts, "0", "dynamic traces: exited")
    dict["instrExec"] = readRun(dir, ts, "0", "dynamic traces: instructions executed")
#   print readRun(dir, ts, "0", "dynamic traces: instr.* dispatched")
    dict["instr/tr"] = readRun(dir, ts, "0", "^dynamic traces: instr/tr dispatched")
#    dict["%complete"] = readRun(dir, ts, "0", "^dynamic traces: % complete (hypothl)")
    dict["%complete"] = readRun(dir, ts, "0", "^dynamic traces: % complete")

    cols = [ "dispatched",  "completed", "exited", "instrExec", "instr/tr", "%complete"]

#     print "cols=",cols
#     print "dict.keys()",dict.keys()

    print dStrOrderedByList(transpose(dict), ts.shortNames(), cols )

