#!/usr/bin/python

# Name: Heri Zhao
# Uniqname: zhaoheri

# Usage
# Doing preprocess for the data set
# takes two argvs
# argv[1] is original input train file name
# argv[2] is svm formatted train file name
# argv[3] is original input test file name
# argv[4] is svm formatted test file name


import sys
import re
import os
import collections
from stemmer import PorterStemmer
import math
import collections

# Tokenize text
def tokenizeText(t):
    t = t.lower()
    t = re.sub('I\'m', 'I am', t)                                       # expand i'm
    t = re.sub('(?<=[a-z])\'re', ' are', t)                             # expand you're, they're, we're
    t = re.sub('n\'t', ' not', t)                                       # expand n't
    t = re.sub('(?<=[a-z])\'s', '', t)                                  # remove 's
    # transform date (01/01/2010 or 01,01,2010 or 01-01-2010) to 01-01-2010 format
    # t = re.sub('((0?[0-9])|(1[1-2]))(/|-|,)(([0-2]?[0-9])|(3[0-1]))(/|-|,)(([0-9]{2})|([0-9]{4}))', daterepl, t)
    t = re.sub('( \.+)|((?<=[0-9])\.(?=[^0-9]))|,|\(|\)|\+|/', ' ', t)  # remove redundant . , ( ) /
    t = re.sub('(?<=[^0-9])\.(?=[0-9])', '. ', t)                       # separate number from abbreviation
    t = re.sub('((?<=[^a-z0-9])-)|(-(?=[^a-z0-9]))', '', t)             # remove - which are not between words and dates
    t = re.sub('\.|\;|\,|\!|\?|\:|[0-9]', ' ', t)
    return re.split('\s+', t.strip())

def removeStopwords(tokenList):
	for stopword in stopwordsList:
		tokenList = filter(lambda x : x != stopword, tokenList)
	return tokenList

def stemWords(tokenList):
	ps = PorterStemmer()
	i = 0
	while i < len(tokenList): 
		tokenList[i] = ps.stem(tokenList[i], 0, len(tokenList[i])-1)
		i += 1
	return tokenList

def processing(inputFile):
	ifile = open(inputFile)
	count = 0
	contentMap = {} # line number -> tokens set
	wordsMap = {} # token -> frequency
	classList = []
	classMap = {} # classname dict: line number -> class name
	for line in ifile.readlines():
	    line = line[1:-1]
	    lineclass = line.split("'")[1]
	    classList.append(lineclass)
	    lineContent = line[len(lineclass) + 5 : -2]  
	    tokens = tokenizeText(lineContent)
	    tokens = removeStopwords(tokens)
	    tokens = stemWords(tokens)
	    tokens = list(set(tokens))
	    contentMap[count] = tokens
	    classMap[count] = lineclass
	    count += 1
	    for t in tokens:
	    	if t in wordsMap:
	    		wordsMap[t] += 1
	    	else:
	    		wordsMap[t] = 1

	return count, contentMap, wordsMap, classList, classMap



# read in stop words
ifile = open("stopwords")
line = ifile.readline()
stopwordsList = []
while line:
	line = line.strip()
	stopwordsList.append(line)
	line = ifile.readline()
ifile.close()

# preprocessing training dataset
docNum, contentMap, wordsMap, classList, classMap = processing(sys.argv[1])

wordsMap = dict((key,value) for key, value in wordsMap.iteritems() if value >= 3)
vocabulary = wordsMap.keys()
classList = list(set(classList))

outputFile = sys.argv[2]
ofile = open(outputFile, 'w')
for i in contentMap:
	outputMap = {} # token id -> frequency
	for t in contentMap[i]:
		if t in wordsMap:
			df = math.log10(float(docNum) / float(wordsMap[t]))
			# df = float(wordsMap[t]) / float(docNum)
			outputMap[vocabulary.index(t)] = df
	outputMap = collections.OrderedDict(sorted(outputMap.items()))
	outputStr = ""
	classid = classList.index(classMap[i]) + 1
	outputStr += str(classid) + " "
	for t in outputMap:
		outputStr += str(t+1) + ":" + str(outputMap[t]) + " "
	ofile.write(outputStr + "\n")


# preprocessing for train data set
tmpcount, contentMap, tmpwordsMap, tmpclassList, classMap = processing(sys.argv[3])

outputFile = sys.argv[4]
ofile = open(outputFile, 'w')
for i in contentMap:
	outputMap = {} # token id -> frequency
	for t in contentMap[i]:
		if t in wordsMap:
			df = math.log10(float(docNum) / float(wordsMap[t]))
			# df = float(wordsMap[t]) / float(docNum)
			outputMap[vocabulary.index(t)] = df
	outputMap = collections.OrderedDict(sorted(outputMap.items()))
	outputStr = ""
	classid = classList.index(classMap[i]) + 1
	outputStr += str(classid) + " "
	for t in outputMap:
		outputStr += str(t+1) + ":" + str(outputMap[t]) + " "
	ofile.write(outputStr + "\n")

print vocabulary[0]