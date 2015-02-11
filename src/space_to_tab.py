#!/usr/bin/env python
import sys


def spcace_to_tab(path_to_file):
    out = path_to_file + "tab"
    out = open(out, 'w')
    f = open(path_to_file, 'r')
    l = f.readlines()
    l = [ll.strip() for ll in l]
    l = [ll.split() for ll in l]
    s = set()
    for line in l:
        if line:
            out.write("\t".join(line) + "\n")
        else:
            out.write("\n")

def main():
    spcace_to_tab(sys.argv[1])


if __name__ == "__main__":
    main()