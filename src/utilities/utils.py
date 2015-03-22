#!/usr/bin/env python


def equals(w1, w2):
    suffixes = ['_B', '_M', '_E']
    for suff in suffixes:
        if w1.endswith(suff):
            w1 = w1.replace(suff, "")
        if w2.endswith(suff):
            w2 = w2.replace(suff, "")
    return w1 == w2


def entity2clean_entity(entity):
    suffixes = ['_B', '_M', '_E']
    for suff in suffixes:
        if entity.endswith(suff):
            entity = entity.replace(suff, "")
            return entity
    return entity


def file2data(f):
    f = open(f, 'r')
    data = []
    sentence = []
    k = 0
    for line in f.readlines():
        if not line.strip():
            data.append(sentence)
            sentence = []
        else:
            sentence.append(line.strip().split())
    return data


def data2file(data, f):
    f = open(f + 'new', 'w')
    for sentence in data:
        for line in sentence:
             f.write(" ".join(line) + "\n")
        f.write("\n")