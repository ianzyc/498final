# 498final  
## extractLabel.py:  
The script needs some data file including:


	1) classname_map.csv
	2）items.json

Run python extractLabel.py and the data set will be extracted into two file: test_data and train_data 

## Naive Bayes:  
The script needs some data file including:


	1) ratemyProfessor_1.2/classname_map.csv
	2) ratemyProfessor_1.2/train_data/*
	3) ratemyProfessor_1.2/test_data

Run python naivebayes.py in the command line and the result will be printed in command window.
It will show the final prediction as well as the accuracy.

## Decision Tree:

The script needs data file including:

	1) ratemyProfessor_1.2/classname_map.csv
	2) ratemyProfessor_1.2/train_data
	3) ratemyProfessor_1.2/test_data
	4) ratemyProfessor_1.2/classname_map.csv

Run python decisionTree.py in the command line and the result will be printed in the file DTout.

## SVM:  
To run svm_light, needs data file including:


	1) ratemyProfessor_1.2/train_data
	2) ratemyProfessor_1.2/test_data
	3) svm/classlist

In the 498final/ directory


	1) run preprocess script to convert train_data and test_data to the format svm_light library needs.  
		$ python svm/svm_preprocess.py [input train file] [formatted train file] [input test file] [formated test file]
		example:   
		$ python svm/svm_preprocess.py ratemyProfessor_1.2/train_data svm/train  ratemyProfessor_1.2/test_data svm/test  
	2) run learning althorithm:  
		$./svm/svm_multiclass_linux64/svm_multiclass_learn -c 5000 svm/train svm/model    
	3) run classification althorithm: (the althorithm will automatically give out the accuracy)  
		$./svm/svm_multiclass_linux64/svm_multiclass_classify svm/test svm/model svm/predictions  
		the predictions file is the result in the original format.  
	4) run postprocess script to convert predictions to human readable format  
		$ python svm_postprocess.py [classlist] [predictions] > [output file]  
		example:  
		$ python svm_postprocess.py svm/classlist svm/predictions > svm/predict
