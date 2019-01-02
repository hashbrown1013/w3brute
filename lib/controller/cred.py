#!/usr/bin/env python

# Copyright (c) 2018 W3brute Developers.
# See LICENSE for more details.

import re
import time

from lib.core.common import cetakData
from lib.core.common import createList
from lib.core.common import parseSlice
from lib.core.data import auth
from lib.core.data import credDb
from lib.core.data import defaults
from lib.core.data import konf
from lib.core.exception import W3bruteNextStepException
from lib.core.pydict import PyDict
from lib.core.settings import EMAIL_PATTERN
from lib.utils.text import Spinner

def checkCredential():
    """
    memeriksa jika daftar kredensial sudah diatur
    """
    
    # cek jika kredensial untuk autentikasi standard dan Authorization belum di atur.
    if (auth.IS_STANDARD_AUTH or auth.IS_AUTHORIZATION) and konf.standardCred is None:
        setKredensial()
    
    # cek jika kredensial untuk autentikasi email belum di atur.
    elif auth.IS_EMAIL_AUTH and konf.emailCred is None:
        setKredensial()
    
    # cek jika kredensial alias wordlist belum di atur.
    elif auth.IS_WEBSHELL_AUTH and konf.webShellCred is None:
        setKredensial()

def setKredensial():
    infoMsg = "[INFO] preparing credentials...\n"
    cetakData(infoMsg)
    
    sliceUser = parseSlice(konf.sliceUser)
    slicePass = parseSlice(konf.slicePass)
    usernames = sorted(createList(konf.usernames))
    passwords = sorted(createList(konf.passwords))
    
    # slice object (start) harus kurang dari len(object)
    if sliceUser.start >= len(usernames):
        sliceUser.start = 0
    
    if slicePass.start >= len(passwords):
        slicePass.start = 0
    
    usernames = usernames[sliceUser]
    passwords = passwords[slicePass]
    
    if konf.mixedCred and konf.sqliBypass:
        warnMsg = "[WARNING] if you want to use the '--mixed-cred' option "
        warnMsg += "please do not use the '--sqli-bypass' option\n"
        cetakData(warnMsg)
        
        time.sleep(2) # durasi untuk anda membaca pesan.
        
        infoMsg = "[INFO] SQL injection bypass authentication techniques are disabled\n"
        cetakData(infoMsg)
        
        del konf.sqliBypass
    
    if auth.IS_WEBSHELL_AUTH and (konf.sqliBypass or konf.mixedCred):
        msg = "[ASK] do you want to use "
        msg += "SQL injection bypass authentication technique "
        msg += "on the web shell? (y/N): "
        jawaban = raw_input(msg).lower()
        if jawaban.startswith("n"):
            del konf.sqliBypass
            del konf.mixedCred
    
    if auth.IS_EMAIL_AUTH and not konf.sqliBypass:
        # konfigurasi kredensial untuk autentikasi
        # yang menggunakan email
        domains = createList(defaults.domain)
        
        if not konf.domain:
            msg = "[ASK] do you want to add a domain for email? "
            msg += "(default %s) (Y/n): " % repr(defaults.domain)
            jawaban = raw_input(msg).lower()
            if jawaban.startswith("y"):
                msg = "[#] enter domain (e.g. yahoo.com,mail.org): "
                domen = raw_input(msg).lower().strip()
                if len(domen) > 0:
                    domen = createList(domen)
                    domains.extend(domen)
        
        else:
            domen = createList(konf.domain)
            domains.extend(domen)
        
        domains = sorted(domains)
        infoMsg = "[INFO] adding domain to username...\n"
        cetakData(infoMsg)
        
        maxval = len(usernames) * len(domains)
        suffix = "%(curval)d/%(maxval)d %(percent)d%%"
        spin = Spinner("[INFO] current progress: ", maxval=maxval, suffix=suffix)
        
        _ = []
        
        try:
            for username in usernames:
                for domen in domains:
                    spin.show_progress()
                    
                    if domen.startswith("@"):
                        domen = domen.lstrip("@")
                    
                    if not re.search(EMAIL_PATTERN, username):
                        user = username + "@"
                        user += domen
                        _.append(user)
                    else:
                        _.append(username)
        
        except W3bruteNextStepException:
            pass 
        
        spin.done()
        usernames = _
        del _
    
    if not auth.IS_WEBSHELL_AUTH and konf.mixedCred:
        infoMsg = "[INFO] adding SQL query to username...\n"
        cetakData(infoMsg)
        
        sqliQuery = createList(defaults.sqliQuery)
        maxval = len(usernames) * len(sqliQuery)
        suffix = "%(curval)d/%(maxval)d %(percent)d%%" 
        spin = Spinner("[INFO] current progress: ", maxval=maxval, suffix=suffix)
        
        _ = []
        
        try:
            for username in usernames:
                for query in sqliQuery:
                    spin.show_progress()
                    
                    user = username + query
                    _.append(user)
        
        except W3bruteNextStepException:
            pass
        
        spin.done()
        usernames = _
        del _
    
    if auth.IS_WEBSHELL_AUTH and konf.mixedCred:
        infoMsg = "[INFO] adding SQL query to password...\n"
        cetakData(infoMsg)
        
        wordlist = usernames + passwords
        sqliQuery = createList(defaults.sqliQuery)
        maxval = len(wordlist) * len(sqliQuery)
        suffix = "%(curval)d/%(maxval)d %(percent)d%%" 
        spin = Spinner("[INFO] current progress: ", maxval=maxval, suffix=suffix)
        
        _ = []
        
        try:
            for username in usernames:
                for query in sqliQuery:
                    spin.show_progress()
                    
                    user = username + query
                    _.append(user)
        
        except W3bruteNextStepException:
            pass
        
        spin.done()
        credDb.wordlist = _
        konf.webShellCred = True # konfigurasi jika wordlist telah di atur.
        del _
    
    if konf.sqliBypass:
        # jika opsi --sqli-bypass digunakan
        # maka username dan password akan menggunakan
        # SQL injection query
        sqliQuery = createList(defaults.sqliQuery)
        usernames = sqliQuery
        passwords = sqliQuery
    
    ##########################
    # konfigurasi kredensial #
    ##########################
    
    if auth.IS_WEBSHELL_AUTH and not konf.mixedCred:
        credDb.wordlist = usernames + passwords
        konf.webShellCred = True # ^
    
    if not auth.IS_WEBSHELL_AUTH:
        credDb.passwords = passwords
        
        if auth.IS_EMAIL_AUTH:
            credType = "email"
            # tambahkan konfigurasi emailCred
            # jika username dan password telah di atur.
            # jadi tidak akan mengatur ulang kembali proses
            # penyiapan kredensial (username dan password)
            konf.emailCred = True
        else:
            credType = "standard"
            konf.standardCred = True # ^
        
        credDb[credType] = PyDict()
        credDb[credType].usernames = usernames
        
        del usernames, passwords
    
    infoMsg = "preparing credentials is complete"
    logger.info(infoMsg)
