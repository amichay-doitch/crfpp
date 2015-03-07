#!/usr/bin/env python
import sys, re


def file2data(f):
    ff = open(f, "r")
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
        if len(line.split(" ")) != 4:
            print "bad line found: {0}".format(line)


def main():
    """
    purpose: split output_old\genia_clean_full.txt into three files, and check them all
    """

    data = file2data(sys.argv[1])
    size = len(data)/4
    out = data[0:size]

    outPath = sys.argv[1] + 'quarter'
    write_data_to_path(out, outPath)
    check(outPath)








if __name__ == "__main__":
    main()