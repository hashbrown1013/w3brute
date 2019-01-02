#!/usr/bin/env python

# Copyright (c) 2018 W3brute Developers.
# See LICENSE for more details.

import os
import platform

from lib.core.paths import here
from lib.core.paths import wordlist
from lib.core.paths import webdb
from lib.core.pydict import PyDict
from lib.core.settings import HOMEPAGE
from lib.core.settings import VERSION

# data tipe autentikasi target
auth = PyDict()

# data untuk daftar kredensial sesuai autentikasi.
credDb = PyDict()

# data pengaturan default
defaults = PyDict(
    agent="w3brute/%s (%s) (%s %s; %s) %s/%s" % (VERSION, HOMEPAGE, os.uname()[0], os.uname()[2], platform.architecture()[0], platform.python_implementation(), platform.python_version()),
    timeout=30,
    retries=5,
    delay=3,
    domain="gmail.com",
    usernames=wordlist("usernames.txt"),
    passwords=wordlist("passwords.txt"),
    sqliQuery=webdb("sqliQuery", "list"),
    adminPaths=webdb("adminPaths", "list"),
    outputDir=here("output/"),
    filename="result",
    fileFormat="csv",
    googlePage=1
)

# data html
html = PyDict()

# data konfigurasi
konf = PyDict()

status = PyDict(
    found=bool(), # status informasi jika menemukan akun berpotensi.
    valid=bool() # status informasi jika akun valid (gunakan opsi '--regex-valid').
)

# data target
target = PyDict()
