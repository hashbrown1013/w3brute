#!/usr/bin/env python

# Copyright (c) 2018 W3brute Developers.
# See LICENSE for more details.

import os

from lib.controller.brute import bruteForceAttack
from lib.controller.cred import checkCredential
from lib.controller.scanner import checkScanner
from lib.controller.target import checkTarget
from lib.core.data import defaults
from lib.core.data import konf
from lib.utils.sigint import InterruptHandler

def initOptions(options):
    """
    mengatur nilai opsi ke data konfigurasi
    """
    
    optDict = options.__dict__
    
    if options.targetUrl is not None:
        value = optDict.pop("targetUrl")
        konf.target = (value, False)
    
    elif options.targetFile is not None:
        value = os.path.realpath(optDict.pop("targetFile"))
        konf.target = (value, True)
    
    elif options.googleDork is not None:
        value = optDict.pop("googleDork")
        page = optDict.pop("googlePage")
        konf.target = value, page or defaults.googlePage
        konf.googleSearch = True
    
    for (option, value) in optDict.items():
        if option in defaults.keys():
            if value is None:
                value = defaults[option]
                
                if option in ("timeout", "delay"):
                    value = float(value)
                
                if option == "domain":
                    value = None
                
                konf[option] = value
            
            else:
                
                if option == "outputDir":
                    value = os.path.realpath(value)
                
                konf[option] = value
        
        else:
            konf[option] = value

def init():
    """
    fungsi yang akan dijalankan
    """
    
    InterruptHandler() # mendaftarkan interrupt handler
    checkScanner() # cek opsi scanner
    
    parsed = checkTarget() # cek jika target didukung untuk melakukan bruteforce attack
    parsed.getValidForms() # mendapatkan form yang menuju ke dashboard situs.
    parsed.getTipeAutentikasi() # mendapatkan tipe autentikasi target
    parsed.getParameterForm() # mendapatkan paramater(s) untuk masuk ke situs
    
    checkCredential() # memeriksa daftar kredensial
    bruteForceAttack() # memulai brute force attack 
