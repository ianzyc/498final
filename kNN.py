from os import listdir
from stemmer import PorterStemmer
import sys
import re
import math
    
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

class DocVector:
    def __init__(self):
        self.dict = {}
    def add_token(self, token):
        if token not in self.dict:
          self.dict[token] = 1
        else:
          self.dict[token] += 1

def preprocessTestData(file_name):
    file = open(file_name, 'r')

    doc_list =[] 
    class_list = []

    for line in file.readlines():
        line = line[1:-1]
        line_class = line.split("'")[1]
        line_content = line[len(line_class) + 5 : -2]  
        token = tokenizeText(line_content)
        token = removeStopwords(token)
        token = stemWords(token)
        doc_vec = DocVector()
        for t in token:
            doc_vec.add_token(t)
        doc_list.append(doc_vec)
        class_list.append(line_class)

    return doc_list, class_list

def preprocessTrainData(file_name):
    file = open(file_name, 'r')

    doc_dict = {}

    for line in file.readlines():
        line = line[1:-1]
        line_class = line.split("'")[1]
        line_content = line[len(line_class) + 5 : -2]  
        token = tokenizeText(line_content)
        token = removeStopwords(token)
        token = stemWords(token)
        doc_vec = DocVector()
        for t in token:
            doc_vec.add_token(t)
        doc_dict[doc_vec] = line_class

    return doc_dict

def kNN_predict(train_doc_dict, test_doc_list, k):
    assert k > 0
    result_list = []
    for test_doc in test_doc_list:
        distance_dict = {}
        for train_doc in train_doc_dict:
            distance = 0.0
            for token in train_doc.dict:
                distance += (test_doc.dict.get(token, 0) - train_doc.dict[token]) ** 2
            for token in test_doc.dict:
                if token not in train_doc.dict:
                    distance += test_doc.dict[token] ** 2
            distance = math.sqrt(distance)
            distance_dict[train_doc] = distance
        sorted_dict = sorted(distance_dict, key=distance_dict.get, reverse=True)
        class_dict = {}
        count = k
        for key in sorted_dict:
            if train_doc_dict[key] not in class_dict:
                class_dict[train_doc_dict[key]] = 1
            else:
                class_dict[train_doc_dict[key]] += 1
            count -= 1
            if count == 0:
                break
        result_list.append(sorted(class_dict, key=class_dict.get)[0])
    return result_list

### main function below

if __name__ == '__main__':

    file_dir = 'ratemyprofessor_1.2/'

    train_file_name = file_dir + 'train_data'
    test_file_name = file_dir + 'test_data'

    train_doc_dict = preprocessTrainData(train_file_name)
    test_doc_list, test_class_list = preprocessTestData(test_file_name)
    k = 15
    result_list = kNN_predict(train_doc_dict, test_doc_list, k)
    correct = 0
    for i in range(0, len(result_list)):
        print 'predict: %s\treal: %s' % (result_list[i], test_class_list[i])
        if result_list[i] == test_class_list[i]:
            correct += 1
    print 'Accuracy is %f' % (1.0 * correct / len(test_doc_list))

