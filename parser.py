#! /usr/bin/python
import sys
import os
import json
import math
from collections import defaultdict

questionIndex = sys.argv[1]

def findAndReplace(tree, d):
    # it's a binary tree
    if len(tree)==3:
        findAndReplace(tree[1],d)
        findAndReplace(tree[2],d)
        return
    # it's a unary tree
    if len(tree)==2:
        word = tree[1]
        # infrequent word, replace with _RARE_
        if word in d:
            if d[word]<5:
                tree[1]="_RARE_"

# call like this: python parser.py into_rare input_file output
# take an input_file to get the word/rule counts. Based on the count file, 
# change the infrequent words in the output file into rare
# check whether the input number is correct
if questionIndex == "into_rare" and len(sys.argv)==4:
    inputFile = sys.argv[2]
    outputFile = sys.argv[3]
    # create cfg.counts and build dict based on cfg.counts
    os.system("python count_cfg_freq.py "+ inputFile + "> cfg.counts")
    countFile = open('./cfg.counts','r')
    # traverse through the cfg.counts file, pull out unaryrule that has freq <5
    rare_d = defaultdict(int)
    for l in countFile:
        line = l.strip()
        if line: # nonempty line
            fields = line.split(" ") # split by space
            # unary rule has the following format
            # count UNARYRULE TAG Word
            # We only need to look at UNARYRULE
            if fields[1] == "UNARYRULE":
                count = int(fields[0])
                word = fields[-1]
                # word already in rare_d, add on top of the count
                if word in rare_d:
                    rare_d[word] += count
                else:
                    rare_d[word] = count
            # not UNARYRULE next
            else:
                continue
    # now we obtain a word count dict, go through the parse_train.dat file
    # go through train.dat file and change leaves that has freq<5 into _RARE_
    # make a copy, then work on outputFile directly
    # inputFile=open("./parse_train.dat", 'r')
    inputFile = open(inputFile, 'r')
    outputFile = open(outputFile,'w+')
    # outputFile=open("./parse_train.RARE.dat", 'w+')

    for l in inputFile:
        tree = json.loads(l)
        findAndReplace(tree, rare_d)
        outputFile.write(json.dumps(tree)+'\n')

def constructTree(wordList, bp_dict, start, end, head_nonterm):
    # for case bp(1,1,Dt)
    if start==end:
        return [head_nonterm, wordList[start]]
    else:
        (X,Y,Z,s)=bp_dict[(start,end,head_nonterm)]
        return [head_nonterm, constructTree(wordList, bp_dict, start, s, Y),
                constructTree(wordList, bp_dict, s+1, end, Z)]

def CKY(sentence, bi_dict, unary_dict, nonterm_dict, lexicon_list):
    pi_dict = defaultdict(float)
    bp_dict = defaultdict()
    # break sentences into words
    wordList = sentence.split()
    sentence_len = len(wordList)
    nonterm_list = nonterm_dict.keys()
    binary_list = bi_dict.keys()
    sentence_cp = sentence
    wordList_cp = sentence_cp.split()

    for index in range(sentence_len):
        if wordList[index] not in lexicon_list:
            wordList[index] = "_RARE_"

    # initialization
    for i in range(0, sentence_len):
        for X in nonterm_list:
            # if X->xi exist
            if (X, wordList[i]) in unary_dict:
                pi_dict[(i,i,X)] = unary_dict[(X, wordList[i])]
            else:
                pi_dict[(i,i,X)] = 0
    # main algorithm
    for l in range(1, sentence_len):
        for i in range(0, sentence_len-l):
            j = i+l
            for X in nonterm_list:
                maxPi = 0
                tmp_bp = None
                # X->YZ in R
                for r in binary_list:
                    if r[0] == X:
                        (_, Y, Z) = r
                        for s in range(i,j):
                            curPi = bi_dict[r] * pi_dict[(i, s, Y)] * pi_dict[(s + 1, j, Z)]
                            # if l==1 and i ==0 and s==0 and j==1:
                            #     print "left"+str(pi_dict[(i, s, Y)])
                            #     print "right"+str(pi_dict[(s + 1, j, Z)])
                            #     # print "total"+str(curPi)
                            # print curPi
                            if curPi>= maxPi:
                                maxPi = curPi
                                tmp_bp = (X,Y,Z,s)
                    else:
                        continue
                # print maxPi
                pi_dict[(i,j,X)]=maxPi
                bp_dict[(i,j,X)]=tmp_bp

    if pi_dict[(0, sentence_len - 1, "S")] != 0:
        # print "returning nonzero pi"
        parse_tree = constructTree(wordList_cp, bp_dict, 0, sentence_len-1, "S")
        return parse_tree
    else:
        maxPi = float("-inf")
        head = None
        for X in nonterm_list:
            if pi_dict[(0, sentence_len-1, X)] >= maxPi:
                maxPi = pi_dict[(0, sentence_len-1, X)]
                head = X
        parse_tree = constructTree(wordList_cp, bp_dict, 0, sentence_len-1, head)
        return parse_tree

# use CKY algorithm to parse sentences into corresponding parse trees
# Parsing
if (questionIndex == "parse" or questionIndex=='parse_vert') and len(sys.argv) ==5:
    train_data = sys.argv[2]
    test_data = sys.argv[3]
    predict_file = sys.argv[4]
    # first, we need to build dict for binaryrule, unaryrule and Nonterm
    if (questionIndex == "parse"):
        # create cfg.RARE.counts based on the new parse_train.RARE.dat
        os.system("python count_cfg_freq.py parse_train.RARE.dat > cfg.RARE.counts")
        countFile = open('./cfg.RARE.counts', 'r')
    else:
        os.system("python count_cfg_freq.py parse_train_vert.RARE.dat > cfg_vert.RARE.counts")
        countFile = open('./cfg_vert.RARE.counts')
    # binary dict with (X,Y1,Y2) as its key and Count(X->Y1,Y2) as its value
    # unary dict with (X,w) as its key and count(X->w) as its value
    # nonterm dict with X as its key and count(X) as its value
    bi_dict = defaultdict(float)
    unary_dict = defaultdict(float)
    nonterm_dict = defaultdict(int)
    for l in countFile:
        line = l.strip()
        if line: # nonempty line
            fields = line.split(" ") # split by space
            # nonterm has the following format
            # count NONTERMINAL X
            if fields[1] == "NONTERMINAL":
                count = int(fields[0])
                nonterm = fields[-1]
                nonterm_dict[nonterm]=count
            # unary rule has the following format
            # count UNARYRULE TAG Word
            elif fields[1] == "UNARYRULE":
                count = int(fields[0])
                nonterm = fields[2]
                word = fields[-1]
                # By the time we processing UNARYRULE, we should have nonterm_dict builtup already
                unary_dict[(nonterm, word)] = count*1.0/nonterm_dict[nonterm]

            # Binary rule has the following format
            # count BINARYRULE X Y1 Y2
            else:
                count = int(fields[0])
                X = fields[2]
                Y1 = fields[3]
                Y2 = fields[4]
                # By the time we processing BINARYRULE, we should have nonterm_dict builtup already
                bi_dict[(X,Y1,Y2)] = count*1.0/nonterm_dict[X]
    udk = unary_dict.keys()
    lexicon_list=[]
    for key in udk:
        lexicon_list.append(key[1])
    # Now we have q(X->Y1 Y2) and q(X->w), we shall begin working on CKY
    test_data = open(test_data, 'r')
    predict_file = open(predict_file, 'w+')
    for l in test_data:
        parse_tree = CKY(l, bi_dict, unary_dict, nonterm_dict, lexicon_list)
        predict_file.write(json.dumps(parse_tree))
        predict_file.write('\n')



