# -*- coding: utf-8 -*-
"""json formater
    <src_path> <output_file>
"""
import os,sys
import json

def formater(src_path, des_file):
    if not os.path.exists(src_path): return
    dir = os.path.dirname(os.path.abspath(src_path))
    des_path = os.path.join(dir, des_file)
    with open(src_path) as fp:
        content = json.load(fp)
    with open(des_path, 'w') as of:
        json.dump(content, of, indent=4)
    print 'output to %s done'%des_file
    
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print __doc__
        sys.exit(1)
    formater(sys.argv[1],sys.argv[2])
    