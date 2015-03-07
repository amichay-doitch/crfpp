#!/usr/bin/env python
import sys
from nner_adjuster import file2data

def clean_suffix(entity):
    suffixes = ['_B', '_M', '_E']
    for suff in suffixes:
        if entity.endswith(suff):
            entity = entity.replace(suff, "")
            return entity
    return entity

def analyze(data):
    map = dict()
    for sentence in data:
        for line in sentence:
            sentence, shape, entity = line
            entity = clean_suffix(entity)
            if entity not in map:
                map[entity] = 0
            map[entity] += 1
    return map

def show_map(map):
    summ = sum([map[key] for key in map])
    for key in map:
        print key, map[key], float(map[key])/summ

def main():
    f = sys.argv[1]
    data = file2data(f)
    map = analyze(data)
    show_map(map)

if __name__ == "__main__":
    main()