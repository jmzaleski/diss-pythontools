#!/usr/bin/python

# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4 -*-

# reads files left behind from running our modified jamvm under monster
# reads monster .txt session files and extracts the PMC names and totals

from TestEnv       import TestEnv

SFMT="%15s"    #stolen from RunResultReaderVisitor
FFMT="%15.1f"

import re

from DictOfDict import dStrRow, dStrRowOrderedByList, dStrHeaderLine

# from livio's parse-raw.sh 
#    read -u 3 t1 t2 log_entry t3 cycles run insts dcache reject lsu erat gct fxu fpu l2 l2_mod mem icache l2_shared br eeoff intpend compl extints

#-------------------------------------------------------------------------------------+
#  Completion Cycles  |                                                               |
#---------------------+---------------------------------------------------------------+
#  GCT empty  Cycles  |  I-cache miss                                                 |
#                     |  Branch misprediction                                         |
#                     |  Other GCT                                                    |
#---------------------+---------------------------------------------------------------+
#                     |                          |                 |                  |
#  Completion Stall   |  Stall by LSU            | Stall by Reject |    ERAT miss     |
#                     |                          |                 |                  |
#            Cycles   |                          |                 |    Other reject  |
#                     |                          |----------------------------------  |
#                     |                          | Stall by D cache miss              |
#                     |                          |                                    |
#                     |                          | Stall by LSU basic latency         |
#                     |-------------------------------------------------------------- +
#                     | Stall by FXU instruct                                         |
#                     |                                                               |
#                     | Stall by FPU instruct                                         |
#                     |                                                               |
#                     | Completion stalled by some other thing                        |
#-------------------------------------------------------------------------------------+


# presumably actually from one of Livio's kernel source files:

# 1:EVENT_GP970_CYC                       cycles
# 2:EVENT_GP970_RUN_CYCLE				  run
# 3:EVENT_GP970_INST_CMPL				  insts
# 4:EVENT_GP970_COMPL_STALL_DCACHE_MISS	  dcache	   data cache misses
# 5:EVENT_GP970_COMPL_STALL_REJECT		  reject	   erat miss reject
# 6:EVENT_GP970_COMPL_STALL_LSU			  lsu		   load store unit
# 7:EVENT_GP970_COMPL_STALL_ERAT_MISS	  erat		   erat misses
# 8:EVENT_GP970_GCT_EMPTY				  gct		   global completion queue empty stall
# 9:EVENT_GP970_COMPL_STALL_FXU			  fxu		   stalls on fixed point unit
# 10:EVENT_GP970_COMPL_STALL_FPU		  fpu		   stalls float unit
# 11:EVENT_GP970_DATA_FROM_L2			  l2		   number of l2 accesses
# 12:EVENT_GP970_L2_MISS_MODIFIED		  l2_mod	   number of remote l2 accesses (modified by someone)
# 13:EVENT_GP970_DATA_FROM_MEM			  mem		   number of accesses that missed both levels of cache
# 14:EVENT_GP970_GCT_EMPTY_ICACHE_MISS	  icache	   instruction cache misses
# 15:EVENT_GP970_L2_MISS_SHARED			  l2_shared	   shared with another l2
# 16:EVENT_GP970_GCT_EMPTY_BR_MPRED		  br           branch mispredicts

# 17:EVENT_GP970_EE_OFF
# 18:EVENT_GP970_EE_OFF_EXT_INT
# 19:EVENT_GP970_GRP_CMPL
# 20:EVENT_GP970_EXT_INT


class GPULResults:
    "describes the totals of the events of a GPUL run"

    def __init__(self) :
        #just init to 8 strings
        self.dict = {}

		#raw data read out of gpul files, derived data calculated by this class
		# first four fields not useful data
		# "t1", "t2", "log_entry", "t3",

		self.RAW_DATA_LAB_LIST=(
			"cycles",          # like elapsed time
			"run",             # cycles running. non idle
			"insts",           # number of instructions executed
			"dcache",          # stalls due data cache misses
			"reject",          # stalls due to loads and stores are rejected for various reasons, for instance due to erat miss
			"lsu",             
			"erat",            # reject cycles due to missing Effective to Real Address Translation cache
			"gct",             # cycles stalled while global completion table is empty.
			"fxu",             # fixed unit
			"fpu",             # float unit
			"l2", "l2_mod", "mem",
			"icache",          # instruction cache
			"l2_shared",
			"br",              # branch mispredicts. I think actually
			"eeoff", "intpend", "compl", "extints"
			)

		# these are fields that are calculated from raw data written by gpul

		self.DERIVED_LAB_LIST=(
  			"idle",                # cycles - run
			"other_reject",        # rejects less ERAT rejects
			"other_lsu",           # lsu less dcache and rejects
			"other_gct",           # gct stalls other than icache and br
			"other"                # the leftover cycles
			)

		self.ALL_LAB_LIST= self.RAW_DATA_LAB_LIST + self.DERIVED_LAB_LIST
		
        # the counts that the parse-raw tool writes to files for consumption by gnuplot
		# only some are used by matz bargraph stuff

		self.DAT_FILE=( "br", "compl", "dcache", "erat", "fpu", "fxu", "icache", "idle",
						"other", "other_gct", "other_lsu", "other_reject"
						)

		# names the gnuplot raw data file each field is to be written into
		# fields livio's gnuplot scripts need
		
		
		self.GNUPLOT_DATA_MAP = { "br":            "br_mpred.user.dat",
								  "compl":         "completed.user.dat",
								  "erat":          "erat_stall.user.dat",
								  "other_reject":  "reject_stall.user.dat",
								  "other_lsu":     "other_lsu_stall.user.dat",
								  "dcache":        "dcache_stall.user.dat",
								  "icache":        "icache.user.dat",
								  "fpu":           "fpu_stall.user.dat",
								  "fxu":           "fxu_stall.user.dat",
								  "idle":          "idle.user.dat",
								  "other":         "other.user.dat",
								  "other_gct":     "other_gct.user.dat",
								  }

		# make our own categories of cycles.
		# similar to Livio's gnuplot histograms except that we don't care about
		# lsu erat vs  other_rejects
		# and we don't call out other_gct
		
		self.CYCLE_CLASSES = {
			                  "compl"       : [ "compl"],      # a cycle in which none of the stall counters were implemented
							  "i-cache"     : [ "icache" ],    # gct
							  "br_misp"     : [ "br"  ],       # gct
							  "d-cache"     : [ "dcache" ],    # lsu
							  "basic_lsu"   : [ "reject", "other_lsu"],
							  "fpu"         : [ "fpu" ],       
							  "fxu"         : [ "fxu" ],
							  "other_stall" : [ "other", "other_gct"],
							 }

#							  "idle"        : [ "idle" ],   #drop idle. its just cycles - run

	def matzCategories(self, dict) :
		"return a new dict that lumps together Livio's fields in a coarser way. "
		newd = {}
		for key in self.CYCLE_CLASSES.keys() :
			total = 0.0
			for listele in self.CYCLE_CLASSES[key] :
				total += dict[listele]
			newd[key] = total
		return newd


	def toDescriptionString(self) :
        return "GPUL result"

	def toString(self, prefix, rowTitle) :
        s = prefix
#        s += dStrHeaderLine(self.shortPmcnames)
#        s += dStrRowOrderedByList(self.dict, self.shortPmcnames, rowTitle)
        return s

    def __str__(self) :
		return self.toDescriptionString() + self.toString("GPULs")

	# unlike time -p data, GPUL usefully breaks the run into time
	# periods livio calls "rounds".

	# hence, we keep the round data separate as it enables those
	# totally cool plots showing phases of execution.

	# Groan, worse, rounds come from each CPU in a multi
	# processor. Need to keep track of this in another dimension of our dict of dicts?

	# sample data for 17 rounds on 2 cpu's..

	# OPTR:0 entry   0 pmcs 10000008000 4154434676 3396546602  280529496   13988292 1408010766     816768  888934992  413322450      31128   10410294       9990     534264   58475070      14772  828237030   15455160   11643726 1177334952          6
	# OPTR:0 entry   1 pmcs 10000008000   15372231   11033327    5412516    1550526    5135064      10356    2071398    4239018         12     178848       9972      13350    3208110       6822     364320    8428002    5493162    5012808          0
	# ...
	# OPTR:0 entry  17 pmcs 7420005936 4914329668 4202985616  257802420   25329234 1683183852     922878  986793144  497194440      26544    7815474       6894     521184   68961168       8820  919663836   14446224   10697364 1452690354         18
	# OPTR:1 entry   0 pmcs 10000008000 2284914341 2096003349   50761200   18992484  731942670    3467622  446851788  242035086      13164    3410568      25074      81474   44552592       7860  403622292   12603084    6002628  717319230          0
	# ...
	# OPTR:1 entry  17 pmcs 7510006008   39016808   22935537   11336460    3241344   25082100    1064400    4865502    7337874        678     263856      21366      12744    2549064       9858     564870    6802314    4509048    9621414          0


    def read( self, aFile, SkipThreshold ) :
        """read lines from the file skipping those that don't match OPTR:0.
        each line records one 'round' of events.
		stash away every round into a dictionary of dictionaries. roundDict[n], where
		n is an int, is a dictionary with a string key corresponding to each of livios
		counters.
		Skip any round for which the number of run cycles is less that SkipThreshold of total cycles"""

		roundDict = {}
		for lab in self.RAW_DATA_LAB_LIST :
			roundDict[lab] = 0.0

		# we're assuming 2 cpu's, should be easy to extend

		NCPU = 2

		lines = {}
		for ix_cpu in range(0,NCPU) :
			lines[ix_cpu] = {}

		nround = 0
		ncpu = 0
		num_round = {}
		
		for l in aFile :
			if not re.match("OPTR:" + str(ncpu),l) :
				#print 'line "' + l + "\n" + ' does not match filter: OPTR:"' + str(ncpu) + '"'
				#print "assume this means we on next cpu"
				if  re.match("OPTR:" + str(ncpu+1),l) :
					num_round[ncpu] = nround
					#print "ncpu=", ncpu, "nround=", nround
					ncpu += 1
					nround = 0
				else:
					print "should match next cpu following", ncpu
					print l
					raise "line does not match following cpu"
			#print "assign lines[", ncpu, "][", nround, "]"
			#print l
			lines[ncpu][nround] = l
			nround += 1
			
		num_round[ncpu] = nround

		#print "ncpu=", ncpu, "nround=", nround
		#print "num_round=", num_round
		
		if ncpu + 1 != NCPU :
			raise "whoa, I though we had ", str(NCPU) + " cpus this experiment"

		maxnr = -1
		for k in num_round.keys() :
			if num_round[k] > maxnr :
				maxnr = num_round[k]
		
		self.ncpu = ncpu
		self.nround = nround

		if 0 :
			print "maxnr=", maxnr
			print "repeat lines read from file", aFile,"nround=", nround, "range", range(0,nround)
			for ix_cpu in range(0,NCPU) :
				for ix_round in range(0,len(lines[ix_cpu].keys())) :
 				    print ix_cpu, ix_round
				    #print lines[ix_cpu][ix_round]

		#initialize to zeros..

		roundDict = {}
		for ix_round in range(0,maxnr) :
			roundDict[ix_round] = {}
			for lab in self.RAW_DATA_LAB_LIST :
				roundDict[ix_round][lab] = 0.0


		# now reprocess the input lines in an orderly way
		# (as we know how many rounds and cpus there are)

		for ix_cpu in range(0,NCPU) :
			for ix_round in range(0,num_round[ix_cpu]) :
				ddat = lines[ix_cpu][ix_round].split()
				dat = ddat[4:]   #skip cruft "OPTR:1 entry NN pmcs" at head of each line

			    # paranoid ! make sure we saw as much data as we expected

				if not len(dat) == len(self.RAW_DATA_LAB_LIST) :
					print "RAW_DATA_LAB_LIST len=", len(self.RAW_DATA_LAB_LIST) ,"doesnt match raw data read len=", len(dat)
					raise "RAW_DATA_LAB_LIST doesnt match raw data read"

			    # this is pretty incautious. Livio's tools dump out the counters in a fixed order
				# related to the way gpul is initialized. The RAW_DATA_LAB_LIST saves this order,
				# as copied from Livio's parse-raw data shell script.
				# (i'd feel better if the first line of data were the labels)


				# read the line data into d, a dict keyed by the label livio gave the field
				# xx hack %% matz
				ix = 0
				d = {}
				for datum in dat :
					lab = self.RAW_DATA_LAB_LIST[ix]
					#if ix == 1 :
					#	print "ix=1", ix, "lab=", lab, "datum=", datum
					d[lab] = float(datum)
					ix += 1

				# what if the "run" field is much smaller than the "cycles" field?
				# that's a clue that the round came from an idle CPU of a single threaded benchmarks
				# in which case we should swallow the round.

				ratio = d["run"] / d["cycles"]
				#print "d[cycles]=", d["cycles"], "d[run]=", d["run"], "ratio=", ratio

				if ratio < SkipThreshold :
					print "skip round", ix_round, "on cpu", ix_cpu, "because ratio of run/cycles too small", ratio
					#print "skip", d
					continue

				ix = 0
				for datum in dat :
					lab = self.RAW_DATA_LAB_LIST[ix]
					#print "lines[ix_cpu]=",lines[ix_cpu]
					#print "ix_round", ix_round, "ix=", ix, "lab=", lab, "datum=", datum
					#print lines[ix_cpu].keys()
					#print roundDict.keys()
					roundDict[ix_round][lab] += float(datum)
					ix += 1
					
				#end for ix_round
				
			#end for ix_cpu

		if 0 :
			for ix in range(0,nround):
				print "round ix=", ix
				print roundDict[ix]

	    return roundDict


	def calculate(self, d) :
		"""perform remaining calculations done by Livio's parse-raw.sh.
		Idea is that tool dumps out counters, some of which need to be fixed up or extended a bit
		"""
		#these are the fields we want running totals for.

		for round in d.keys() :
			rawDataDict = d[round]
			for f in self.DERIVED_LAB_LIST :
				if rawDataDict.has_key(f) :
				    print rawDataDict
					raise "hey, raw dict already has field \"" + f + "\""

			# For this setup "run" is only measured in 4/6 groups
			# this has something to do with the way the pmc's are multiplexed
			# that results in only being about to collect run cycles 4/6 of the time.

			rawDataDict["run"] *= 6.0/4.0

			# idle is by defn cycles NOT running.

			if rawDataDict["cycles"] > rawDataDict["run"] :
				rawDataDict["idle"] = rawDataDict["cycles"] - rawDataDict["run"]
			else:
				rawDataDict["idle"] = 0.0

			# Any rejects other than erat rejects go into other_reject

			if rawDataDict["reject"] > rawDataDict["erat"] :
				rawDataDict["other_reject"] = rawDataDict["reject"] - rawDataDict["erat"]
			else :
				rawDataDict["other_reject"] = 0.0

			# parse-raw codes it equivalently but inconsistently to above:
			#if  rawDataDict["dcache"] + rawDataDict["reject"] < rawDataDict["lsu"] :

			# lsu  = reject + dcache + OTHER_LSU
			# i.e. lsu "basic latency"

			if  rawDataDict["lsu"] > rawDataDict["dcache"] + rawDataDict["reject"]  :
				rawDataDict["other_lsu"] = rawDataDict["lsu"] - rawDataDict["dcache"] - rawDataDict["reject"]
			else:
				rawDataDict["other_lsu"] = 0.0

			# gct = icache + br + OTHER_GCT

			if  rawDataDict["gct"] > rawDataDict["br"] + rawDataDict["icache"] :
				rawDataDict["other_gct"] = rawDataDict["gct"] - rawDataDict["icache"] - rawDataDict["br"]
			else:
				rawDataDict["other_gct"] = 0.0

			# run = compl + lsu + fxu + fpu + gct + OTHER

			rawDataDict["other"] = rawDataDict["run"]  - rawDataDict["lsu"] - rawDataDict["fxu"] - rawDataDict["fpu"] - rawDataDict["gct"] - rawDataDict["compl"]

			d[round] = rawDataDict

		return d


#   from parse-raw.sh

#     if [ $cycles -gt $run ]; then
# 	idle=$((cycles-run))
#     else
# 	idle=0
#     fi
#     echo $idle  >>  $DATADIR/idle.$EXT.dat
#     ((total_idle   +=  $idle))

#     echo $dcache >> $DATADIR/dcache_stall.$EXT.dat
#     ((total_dcache += $dcache))

#     echo $erat   >> $DATADIR/erat_stall.$EXT.dat
#     ((total_erat += $erat))

#     if [ $reject -gt $erat ]; then
# 	other_reject=$((reject-erat));
#     else
# 	other_reject=0
#     fi
#     echo $other_reject >> $DATADIR/reject_stall.$EXT.dat
#     ((total_other_reject += $other_reject))

#     if [ $((dcache+reject)) -lt $lsu ]; then
# 	other_lsu=$((lsu-dcache-reject));
#     else
# 	other_lsu=0;
#     fi
#     echo $other_lsu    >> $DATADIR/other_lsu_stall.$EXT.dat
#     ((total_other_lsu  += $other_lsu))

#     echo $fxu    >> $DATADIR/fxu_stall.$EXT.dat
#     ((total_fxu += $fxu))

#     echo $fpu    >> $DATADIR/fpu_stall.$EXT.dat
#     ((total_fpu += $fpu))

#     echo $br     >> $DATADIR/br_mpred.$EXT.dat
#     ((total_br += $br))

#     echo $icache >> $DATADIR/icache.$EXT.dat
#     ((total_icache += $icache))

#     #######
#     if [ $gct -gt $((br+icache)) ]; then
# 	other_gct=$((gct-icache-br));
#     else
# 	other_gct=0;
#     fi
#     echo $other_gct >> $DATADIR/other_gct.$EXT.dat
#     ((total_other_gct += $other_gct))

#     echo $compl  >> $DATADIR/completed.$EXT.dat
#     ((total_compl += $compl))

#     other=$((cycles-idle-lsu-fxu-fpu-gct-compl))
#     echo $other  >> $DATADIR/other.$EXT.dat
#     ((total_other += $other))

#     ((total_eeoff += $eeoff))
#     ((total_intpend += $intpend))
#     ((total_extints += $extints))

#     ((total_l2        += $l2))
#     ((total_l2_mod    += $l2_mod))
#     ((total_l2_shared += $l2_shared))
#     ((total_mem       += $mem))



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


