#!/usr/bin/env python3
#
# date: 2022-12-28
# version: v0.2
#

import os.path as p
import os
import sys
import re


if(len(sys.argv) < 2):
    print("Usage: %s filename" % sys.argv[0])
    sys.exit(1)

filename = sys.argv[1]
if not p.isfile(filename):
    print("%s is not a file." % filename)
    sys.exit(2)

f_obspath = os.path.realpath(os.path.abspath(filename))
firefox = "win.firefox.exe"

# file://///wsl.localhost/Ubuntu-20.04/tmp/6lHVixCC6.bmp
# file:///C:/Users/yangfeilong/Desktop/MSFAT-spec.pdf
if '/mnt/c' in f_obspath:
    cmdline = "file:///" + f_obspath.replace('/mnt/c','C:')
elif '/mnt/d' in f_obspath:
    cmdline = "file:///" + f_obspath.replace('/mnt/d','D:')
elif '/mnt/e' in f_obspath:
    cmdline = "file:///" + f_obspath.replace('/mnt/e','E:')
else:
    cmdline = "file://///wsl.localhost/Ubuntu-20.04" + f_obspath


os.system("%s %s" %(firefox, cmdline))
