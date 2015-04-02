# write by shuo 65565332
import sys
import os
import operator
import preprocess
import math
import copy

def trainNaiveBayes(trainingdata, traningClass, AllClass):
    ClassDict = {}
    ClassWordCount = {}
    Vocabulary = {}

    ClassFileCount = {}
    FileCount = 0


    for key in trainingdata.keys():
        classID = traningClass[key]
        content = trainingdata[key]

        #file count
        if classID in ClassFileCount.keys():
            ClassFileCount[classID] += 1
        else:
            ClassFileCount[classID] = 1

        FileCount +=1

        #do the word count
        result = preprocess.tokenizeText(content)
        for word in result:
            if classID in ClassWordCount.keys():
                ClassWordCount[classID] += 1
            else:
                ClassWordCount[classID] = 1

            if classID not in ClassDict.keys():
                ClassDict[classID] = {}

            if word in ClassDict[classID].keys():
                ClassDict[classID][word] += 1
            else:
                ClassDict[classID][word] = 1
            Vocabulary[word] = 1

    #do the training result
    result = {}
    vocSize = len(Vocabulary)
    for item in ClassDict.items():
        if item[0] not in result:
            result[item[0]] = {}

        for inneritem in item[1].items():
            result[item[0]][inneritem[0]] = (float(inneritem[1]) + 1) / (ClassWordCount[item[0]] + vocSize)

    #the probability of the file
    FileProb = {}
    for item in ClassFileCount.items():
        FileProb[item[0]] = float(item[1]) / FileCount

    NoExistProb = {}

    for item in ClassFileCount.items():
        NoExistProb[item[0]] = 1 / float(ClassFileCount[item[0]] + vocSize)

    return result, FileProb, NoExistProb

def testNaiveBayes(testData, trainresult, FileProb, NoExistProb, testClass):

    finalResult = {}
    recall = 0
    precision = 0

    for item in testData.items():
        key = item[0]
        content = item[1]
        result = preprocess.tokenizeText(content)

        resultProb = copy.deepcopy(FileProb)
        for fileclass in resultProb.keys():
            for word in result:
                if word in trainresult[fileclass].keys():
                    resultProb[fileclass] *= trainresult[fileclass][word]
                else:
                    resultProb[fileclass] *= NoExistProb[fileclass]

        sorted_dic = sorted(resultProb.items(), key=operator.itemgetter(1), reverse = True)
        finalResult[key] = sorted_dic[0][0]

        #calculate recall
        topFiveList = sorted_dic[0:5]
        topfivelistvalue = []
        for inneritem in topFiveList:
            topfivelistvalue.append(inneritem[0])

        if testClass[item[0]] in topfivelistvalue:
            recall += 0.2
            precision += 1 / float(len(testData))

    return recall, precision, finalResult  


if __name__ == '__main__':

    #get all classes
    classgroup = {}
    groupFile = "ratemyProfessor_1.2/classname_map.csv"
    classfile = open(groupFile, "r")
    linelist = classfile.readlines()
    for line in linelist:
        classgroup[line.split(",")[1]] = True;

    #do the training data
    trainingdata = {}
    trainingclass = {}
    trainingFileName = "ratemyProfessor_1.2/train_data"
    trainingFile = open(trainingFileName,"r")
    traninglines = trainingFile.readlines()
    i = 0
    for line in traninglines:
        line = line[1:-1]
        lineclass = line.split("'")[1]
        lineContent = line[len(lineclass) + 4 : -2]
        trainingdata[i] = lineContent
        trainingclass[i] = lineclass
        i += 1

    #naiveBayes for training data
    trainresult, FileProb, NoExistProb = trainNaiveBayes(trainingdata, trainingclass, classgroup)


    #do the test data
    testData = {}
    testClass = {}
    testFileName = "ratemyProfessor_1.2/test_data"
    testFile = open(testFileName,"r")
    linelist = testFile.readlines()
    i = 0
    for line in linelist:
        line = line[1:-1]
        lineclass = line.split("'")[1]
        lineContent = line[len(lineclass) + 4 : -2]
        testData[i] = lineContent
        testClass[i] = lineclass
        i += 1

    #naiveBayes for test data
    recall, precision, result = testNaiveBayes(testData, trainresult, FileProb, NoExistProb, testClass)

    #calculate accuracy
    accuracy = 0
    for item in result.items():
        print "prediction: " + item[1] + ", correct answer: " + testClass[item[0]]
        if item[1] == testClass[item[0]]:
            accuracy += 1

    print "accuracy: " + str(float(accuracy) / len(testData))
    print "recall: " + str(float(recall) / len(testData))
    print "precision: " + str(float(precision) / len(testData))






