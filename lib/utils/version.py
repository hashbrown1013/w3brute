#!/usr/bin/env python

# Copyright (c) 2018 W3brute Developers.
# See LICENSE for more details. 

import sys

def check():
    IS_PY3K = sys.version_info[0] == 3 # in Python 2.6 there is no major attribute.
    if IS_PY3K:
        msg = "[ERROR] your python version (%s) is not supported. " % sys.version.split()[0]
        msg += "w3brute runs with python version **2.6.x** or **2.7.x** "
        msg += "(visit https://www.python.org/downloads/)"
        exit(msg)
