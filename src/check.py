#!/usr/bin/env python
import sys,re


def check(file):
    f = open(file, 'r')
    lines = [line.strip().split() for line in f.readlines()]
    line_len = len(lines[0])
    print "Line length is {0}".format(line_len)
    for line in lines:
        if not line:
            continue
        if len(line) != line_len:
            print "Bad Line Found!!!"
            print line
            break
    else:
        print "File Checked"


def main():
    file = sys.argv[1]
    check(file)


if __name__ == "__main__":
    main()
