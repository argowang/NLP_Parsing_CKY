# NLP_Parsing_CKY
Use CKY algorithm to parse sentences

## Introduction
The project aims to use CKY algorithm to parse a sentence into corresponding parsing tree.

The original data is fetched from WSJ treebank.

The raw_input has one sentence per line.

The tree generated follows the json encoding scheme.

For example:

raw_input: I love doggie.

tree: ["S", ["NP", ["NP+PRON" I], ["VP", ["V", love], ["NP", doggie]]]

The file parser.py contains all the code

count_cfg_freq.py is a handy tool to count unary rule, binary rule and nonterms.

### Usage

There are two ways to call parser.py

#### Change Infrequent Words into _RARE_

'''
python parser.py inputFile outputFile
'''

By calling parser.py in such a fashion, the program will take a inputFile(which is a file contains trees for training sentences)
and a outputFile(modified trees for training sentences) as input.

The program will count the unary rules of the inputFile, and replace the infrequent words(frequency < 5) into "_RARE" and output to outputFile

#### Actual parsing 

'''
python parser.py parse train_data test_data predict_file
'''

The train_data contains **trees** for training sentences.

The test_data contains **sentences** for test purpose.

The predict_file is the directory of the output.

The program will first generate a count file using train_data. Then use the CKY algorithm to parse the test_data into trees, then output to predict_file

The program is compatible with train_data that undergoes markov verticalization. But the run time will be significantly longer.

### Performance

#### Train data without markov verticalization

Trained on 5322 sentences/trees. Test on 244 sentences.

![alt text](https://s1.postimg.org/16cs7pm1q7/parser_eval_without_markov_vert.png)

#### Train data with markov verticalization

Trained on 5322 sentences/trees. Test on 244 sentences.

![alt text](https://s1.postimg.org/57orm3pxdb/parser_eval_with_markov_vert.png)
