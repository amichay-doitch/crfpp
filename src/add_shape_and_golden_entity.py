#!/usr/bin/env python
import re

INPUT = "../output/out.txt"
OUTPUT = "../output/out_shaped.txt"

def file2data(f):
    ff = open(f,"r")
    data = []
    sentence = []
    for line in ff.readlines():
        if re.search('[a-zA-Z]', line):
            sentence.append(line.strip())
        else:
            data.append(sentence)
            sentence = []
    return data


def word_shape(word):
    trace = ""
    for letter in word:
        if letter.isupper():
            trace += "X"
        elif letter.islower():
            trace += "x"
        elif letter.isdigit():
            trace += "d"
        else:
            trace += letter
    shape = ""
    current = 0
    for match in re.finditer(r"((x)\2{2,})", trace):
        #print trace[current:match.start()],trace[match.start():match.end()]
        shape += trace[current:match.start()+3]
        current = match.end()
    shape += trace[current:]
    return shape
    


def add_shape_to_data(data):
    shaped_data = []
    sentenceShaped = []
    for sentence in data:
        for line in sentence:
            if not re.search('[a-zA-Z]', line):
                continue
            word = line.split()[0]
            tag = line.split()[1]
            wordShape = word_shape(word)
            sentenceShaped.append((" ".join((word, tag, wordShape, tag))))
        shaped_data.append(sentenceShaped)
        sentenceShaped = []
    return shaped_data


def write_data(data):
    out = open(OUTPUT, 'w')
    for sentence in data:
        for line in sentence:
            out.write(line + "\n")
        out.write("\n")
    print "Output file in {0}".format(OUTPUT)

def main():
    data = file2data(INPUT)
    data = add_shape_to_data(data)
    write_data(data)


if __name__ == "__main__":
    main()
