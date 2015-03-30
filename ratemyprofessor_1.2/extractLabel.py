"""
EECS 498 Final Project 
Extract Label from Original Class Names
Yicong Zhang (ianzyc@umich.edu)
"""
import json
import csv
import random

class_dict = {}
prof_dict = {}


# read classname map (csv file)
f = open('classname_map.csv')
csv_f = csv.reader(f)
for line in csv_f:
	class_abbr = str(line[0]).lower()
	class_full = str(line[1])
	class_dict[class_abbr] = class_full
f.close()

# read json file
data_file = open('items.json')    
data = json.load(data_file)

# find all professors, store in prof_dict
for line in data:
	prof_name = str(line['profName']).strip()
	prof_dict[prof_name] = 0

# use 5% professors as test professors, construct test_prof_dict
test_prof_num = len(prof_dict) / 20
test_prof_dict = {}
for i in range(0, test_prof_num):
	prof = random.choice(prof_dict.keys())
	test_prof_dict[prof] = 0
	del prof_dict[prof]

# loop through all raw data
train_data = []
test_data = []
for line in data:
	class_name = str(line['className']).strip()
	prof_name = str(line['profName']).strip()
	review = line['review'].encode('ascii', 'ignore')
	if class_name in class_dict:
		if prof_name in prof_dict:
			train_data.append([class_dict[class_name], review])
		else:
			test_data.append([class_dict[class_name], review])

# output train_data and test_data
f_train = open('train_data', 'wt')
for t in train_data:
	print >> f_train, t
f_train.close()

f_test = open('test_data', 'wt')
for t in test_data:
	print >> f_test, t
f_test.close()
