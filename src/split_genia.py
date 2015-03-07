#!/usr/bin/env python
import sys, re
INPUT = "../output_new/out_shaped.txtnew"

def file2data(f):
    """
    :param f: file with format:
    word1 tag1
    word2 tag2

    word3 tag3
    word4 tag4
    :return: data:
    data = [
    [[word1, tag1], [word2, tag2]],
    [[word3, tag3], [word4, tag4]],
    ]
    """
    ff = open(f,"r")
    data = []
    sentence = []
    for line in ff.readlines():
        if re.search('[a-zA-Z]', line):
            sentence.append(line)
        else:
            data.append(sentence)
            sentence = []
    return data


def write_data_to_path(data, path):
    f = open(path, 'w')
    for sentence in data:
        for line in sentence:
            f.write(line)
        f.write("\n")

def check(pathToFile):
    print "Checking path {0}".format(pathToFile)
    f = open(pathToFile, 'r')
    for line in f.readlines():
        if line == "\n":
            continue
        if len(line.split(" ")) != 3:
            print "bad line found: {0}".format(line)


def main():
    """
    purpose: split output_old\genia_clean_full.txt into three files, and check them all
    """
    data = file2data(INPUT)
    testSize = len(data)/10
    test = data[0:testSize]
    develop = data[testSize:2*testSize]
    train = data[2*testSize:]
    testPath = "../output_new/genia_test.txt"
    developPath = "../output_new/genia_develop.txt"
    trainPath = "../output_new/genia_train.txt"
    write_data_to_path(test, testPath)
    write_data_to_path(develop, developPath)
    write_data_to_path(train, trainPath)
    check(testPath)
    check(developPath)
    check(trainPath)





if __name__ == "__main__":
    main()