#!/usr/bin/env python
import os
import sys
# word gold estimated

def analyze(log):
    f = open(log, 'r')
    l_f = f.readlines()
    number_of_correct_constituents_in_proposed_parse = 0
    number_of_constituents_in_proposed_parse = 0
    number_of_constituents_in_golden_parse = 0
    empty = 0
    sentences = 0
    for line in l_f:
        s_line = line.split()
        if not s_line:
            sentences += 1
            continue
        try:
            if s_line[-2] == s_line[-1] and s_line[-2] != "NE":
                number_of_correct_constituents_in_proposed_parse += 1
            if s_line[-1] != "NE":
                number_of_constituents_in_proposed_parse += 1
            if s_line[-2] != "NE":
                number_of_constituents_in_golden_parse += 1
        except Exception as e:
            empty += 1
        #print e.message
        #print s_line
    print "empty:", empty
    print "number of sentences", sentences
    print "number_of_correct_constituents_in_proposed_parse:", number_of_correct_constituents_in_proposed_parse
    print "number_of_constituents_in_proposed_parse:", number_of_constituents_in_proposed_parse
    print "number_of_constituents_in_golden_parse:", number_of_constituents_in_golden_parse
    precision = float(number_of_correct_constituents_in_proposed_parse) / number_of_constituents_in_proposed_parse
    recall = float(number_of_correct_constituents_in_proposed_parse) / number_of_constituents_in_golden_parse

    print "precision:", precision
    print "recall:", recall
    F1 = 2 * precision * recall / (precision + recall)
    print "F1:", F1


def main():
    log = sys.argv[1]
    analyze(log)


if __name__ == "__main__":
    main()