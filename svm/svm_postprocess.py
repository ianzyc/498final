#!/usr/bin/python

# Name: Heri Zhao
# Uniqname: 8824 6454

import sys
import re
import os
import collections
import math
import collections


classlist = []
ifile = open(sys.argv[1])
for line in ifile.readlines():
	classlist.append(line[0:-1])

ifile = open(sys.argv[2])
classid = []
for line in ifile.readlines():
	p = line.find(" ")
	line = line[0:p]
	classid.append(int(line) - 1)

realClass = []
ifile = open(sys.argv[3])
for line in ifile.readlines():
    line = line[1:-1]
    lineclass = line.split("'")[1]
    realClass.append(lineclass)

resClass = []

for i in classid:
	resClass.append(classlist[i])

for i in range(0, len(resClass)):
	print "predict: " + resClass[i] + "	real: " + realClass[i] 