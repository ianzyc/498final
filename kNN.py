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

class InvertedIndex:
  def __init__(self):
    self.tf_dict = {}
    self.idf_dict = {}
  def add_token(self, token, id):
    if token not in self.tf_dict:
      self.tf_dict[token] = {id: 1}
    else:
      if id not in self.tf_dict[token]:
        self.tf_dict[token][id] = 1
      else:
        self.tf_dict[token][id] += 1
  def calculate_idf(self, N):
    for token in self.tf_dict:
      self.idf_dict[token] = math.log10(float(N) / len(self.tf_dict[token]))

def preprocessTrainData(file_name):
    file = open(file_name, 'r')

    inverted_class_dict = {} # map of class to a list of doc id
    inverted_index = InvertedIndex()

    doc_id = 0
    for line in file.readlines():
        line = line[1:-1]
        line_class = line.split("'")[1]
        line_content = line[len(line_class) + 5 : -2]  
        token_list = tokenizeText(line_content)
        token_list = removeStopwords(token_list)
        token_list = stemWords(token_list)
        for t in token_list:
            inverted_index.add_token(t, doc_id)
        if line_class not in inverted_class_dict:
            inverted_class_dict[line_class] = [doc_id]
        else:
            inverted_class_dict[line_class].append(doc_id)
        doc_id += 1
    inverted_index.calculate_idf(doc_id)
    doc_max_tfs = {}
    for token in inverted_index.tf_dict:
        for id in inverted_index.tf_dict[token]:
            if id not in doc_max_tfs:
                doc_max_tfs[id] = inverted_index.tf_dict[token][id]
            elif doc_max_tfs[id] < inverted_index.tf_dict[token][id]:
                doc_max_tfs[id] = inverted_index.tf_dict[token][id]
    doc_weights_dict = {} # all doc vectors
    for token in inverted_index.tf_dict:
        for id in inverted_index.tf_dict[token]:
            if id not in doc_weights_dict:
                doc_weights_dict[id] = {}
            doc_max_tf = doc_max_tfs[id]
            doc_weights_dict[id][token] = inverted_index.tf_dict[token][id] * inverted_index.idf_dict[token] / doc_max_tf
    # normalize all doc vectors
    for id in doc_weights_dict:
        length_doc = 0.0
        for token in doc_weights_dict[id]:
            length_doc += doc_weights_dict[id][token] ** 2
        length_doc = math.sqrt(length_doc)
        for token in doc_weights_dict[id]:
            doc_weights_dict[id][token] /= length_doc
    class_vec_dict = {}
    for _class in inverted_class_dict:
        class_vec = {} # class vector
        for id in inverted_class_dict[_class]:
            if id not in doc_weights_dict:
                continue
            for token in doc_weights_dict[id]:
                if token not in class_vec_dict:
                    class_vec[token] = doc_weights_dict[id][token]
                else:
                    class_vec[token] += doc_weights_dict[id][token]
        class_vec_dict[_class] = class_vec

    file.close()
    return inverted_index, class_vec_dict

def preprocessTestData(file_name, inverted_index):
    file = open(file_name, 'r')

    class_list = []
    test_vec_list = []

    for line in file.readlines():
        line = line[1:-1]
        line_class = line.split("'")[1]
        line_content = line[len(line_class) + 5 : -2]  
        token_list = tokenizeText(line_content)
        token_list = removeStopwords(token_list)
        token_list = stemWords(token_list)
        test_tf_dict = {}
        for token in token_list:
            if token not in inverted_index.tf_dict:
                continue
            if token in test_tf_dict:
                test_tf_dict[token] += 1
            else:
                test_tf_dict[token] = 1
        test_idf_dict = {}
        for token in test_tf_dict:
            test_idf_dict[token] = inverted_index.idf_dict[token]
        test_weight_dict = {}
        for token in test_tf_dict:
            q_max_tf = max(test_tf_dict.values())
            test_weight_dict[token] = test_tf_dict[token] * test_idf_dict[token] / q_max_tf
        test_vec_list.append(test_weight_dict)
        class_list.append(line_class)

    file.close()
    return test_vec_list, class_list

def kNN_predict(class_vec_dict, test_vec_list):
    result_list = []
    for test_vec in test_vec_list:
        score_dict = {}
        for _class in class_vec_dict:
            score = 0.0
            len_test = 0.0
            len_train = 0.0
            for token in test_vec:
                score += test_vec[token] * class_vec_dict[_class].get(token, 0)
                len_test += test_vec[token] ** 2
            len_test = math.sqrt(len_test)
            for token in class_vec_dict[_class]:
                len_train += class_vec_dict[_class][token] ** 2
            len_train = math.sqrt(len_train)
            if score != 0:
                score /= len_test
                score /= len_train
            else:
                score = 0.0
            score_dict[_class] = score
        result_list.append(sorted(score_dict, key=score_dict.get, reverse=True)[0:5])
    return result_list

### main function below

if __name__ == '__main__':

    file_dir = 'ratemyprofessor_1.2/'

    train_file_name = file_dir + 'train_data'
    test_file_name = file_dir + 'test_data'

    inverted_index, class_vec_dict = preprocessTrainData(train_file_name)
    test_vec_list, test_class_list = preprocessTestData(test_file_name, inverted_index)
    result_list = kNN_predict(class_vec_dict, test_vec_list)
    correct = 0
    precision = 0.0
    recall = 0.0
    for i in range(0, len(result_list)):
        print 'predict: %s\treal: %s' % (result_list[i][0], test_class_list[i])
        if test_class_list[i] in result_list[i]:
            precision += 0.2
            recall += 1
        if result_list[i][0] == test_class_list[i]:
            correct += 1
    print 'Accuracy is %f' % (1.0 * correct / len(test_vec_list))
    print 'Precision is %f' % (precision / len(test_vec_list))
    print 'Recall is %f' % (recall / len(test_vec_list))

