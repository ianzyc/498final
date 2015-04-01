from os import listdir
from stemmer import PorterStemmer
import sys
import re
import math
import csv
    
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

def removeStopwords(listTokens):
    data = open("stopwords.txt").read().replace('\n', ' ');
    # store stop words
    stopWords = []
    stopWords = re.split('\s+', data)
    stopWords = filter(None, stopWords)

    # add non-stopwords to result
    result = []
    for t in listTokens:
        if t not in stopWords:
            result.append(t)
    return result

def stemWords(listTokens):
    ps = PorterStemmer()
    stemmedTokens = []
    for t in listTokens:
        stemmedTokens.append(ps.stem(t, 0, len(t)-1))
    return stemmedTokens

def getClassname(classnameFile):
    classname = {} # classname dict.
    index = 0
    f = open(classnameFile)
    csv_f = csv.reader(f)
   
    for line in csv_f: 
        name = str(line[1])
        if name not in classname:
            classname[name] = index
            index += 1
    f.close()

    return classname

def getVocabulary(trainFileName):
    vocabulary = {} # vocabulary dict.
    index = 0
    trainFile = open(trainFileName, 'r')

    for line in trainFile.readlines():
        line = line[1:-1]
        lineclass = line.split("'")[1]
        lineContent = line[len(lineclass) + 5 : -2]  
        token = tokenizeText(lineContent)
        token = removeStopwords(token)
        token = stemWords(token)
        for t in token:
            if t not in vocabulary:
                vocabulary[t] = index
                index += 1
            
    return vocabulary

### main function below

if __name__ == '__main__':

    # get all classes
    classgroup = {}
    groupFile = "ratemyProfessor_1.2/classname_map.csv"
    classfile = open(groupFile, "r")
    linelist = classfile.readlines()
    for line in linelist:
        classgroup[line.split(",")[1]] = True;

    fileDir = 'ratemyProfessor_1.2/'

    trainFileName = fileDir + '/train_data'
    testFileName = fileDir + '/test_data'
    classnameFile = fileDir + '/classname_map.csv'

    classname = getClassname(classnameFile)
    vocabulary = getVocabulary(trainFileName)

