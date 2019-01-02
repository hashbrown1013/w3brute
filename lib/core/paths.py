#!/usr/bin/env python

# Copyright (c) 2018 W3brute Developers.
# See LICENSE for more details.

import os

BASE_PATH = str()
def addBasePath(path):
    """
    path w3brute
    """
    
    global BASE_PATH
    BASE_PATH = path

# lokasi path (data) w3brute
here = lambda path: os.path.join(BASE_PATH, path)
wordlist = lambda filename: here("data/wordlist.zip;" + filename)
webdb = lambda table, column: here("data/web.db>%s;%s" % (table, column))
