#!/usr/bin/env python
import sys
import os



def test_passed(status_file):
    d = dict()
    f = open(status_file, 'r')
    for line in f.readlines():
        line = line.strip().split("%%")
        d[line[0]] = line[1]
    status = d['fubstatus'] if 'fubstatus' in d else "No status found"
    if status.lower() != 'passed':
        return False
    return True
    
        
def reg_passed(reg_dir):
    if not os.path.isdir(reg_dir):
        return False
    for root, dirs, files in os.walk(reg_dir):
        for file in files:
            if file == "steps.status":
                if not test_passed(os.path.join(root, file)):
                    return False
    return True
                

def main():
    try:
        reg_dir = sys.argv[1]
    except:
        raise Exception('No input given')
    if not reg_passed(reg_dir):
        raise Exception('fail')
    print "Passed"
         
         
if __name__ == "__main__": 
    main()
    
