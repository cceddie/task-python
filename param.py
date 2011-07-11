#!/usr/bin/python

import sys

#for arg in sys.argv:
#    print arg

print sys.argv

    
try:
    sys.argv[1]
except:
    print 'nothing passed'
else:
    print "woot"
    






