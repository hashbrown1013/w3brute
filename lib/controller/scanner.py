#!/usr/bin/env python

# Copyright (c) 2018 W3brute Developers.
# See LICENSE for more details.

import os
import re

from lib.core.common import cetakData
from lib.core.common import createList
from lib.core.common import getNewUrl
from lib.core.common import getQuery
from lib.core.common import pindahBaris
from lib.core.common import parseDbSyntax
from lib.core.data import konf
from lib.core.data import target
from lib.core.exception import W3bruteNextStepException
from lib.core.exception import W3bruteSkipTargetException
from lib.core.settings import ADMIN_PAGE_RESPONSE
from lib.core.settings import SQL_PAYLOAD
from lib.core.settings import SQL_ERROR_MESSAGE
from lib.request.connect import UserAgent
from lib.utils.text import Progress

def checkScanner():
    """
    memeriksa opsi scanner
    """
    
    if konf.sqliScanner:
        try:
            sqliScanner()
        except W3bruteNextStepException:
            pass
    
    if konf.adminScanner:
        adminScanner()

def adminScanner():
    infoMsg = "[INFO] find the admin page...\n"
    cetakData(infoMsg)
    
    pbar = Progress("[INFO] testing page -> ")
    
    found = False
    adminPaths = createList(konf.adminPaths)
    for admin in adminPaths:
        admin = "/" + admin.strip()
        
        pbar.write(admin)
        
        newurl = getNewUrl(target.URL) + admin
        response = UserAgent.open(newurl)
        
        if response.code in ADMIN_PAGE_RESPONSE:
            pbar.newline("[INFO] admin page: {} (valid)")
            target.URL = newurl
            found = True
            break
        
        pindahBaris()
        
    pbar.finish()
    
    if not found:
        filename = os.path.basename(konf.adminPaths)
        if re.search(r"web.db", filename):
            filename = parseDbSyntax(filename)[0]
        
        criMsg = "admin login page not found in database %s" % repr(filename)
        logger.critical(criMsg)
        
        raise W3bruteSkipTargetException
    
    else:
        pass

def sqliScanner():
    """
    SQL injection scanner vulnerability
    untuk mengetahui jika target rentan terhadap SQL injection
    dan biasanya rentan juga di bypass login.
    """
    
    infoMsg = "[INFO] detecting bug SQL injection...\n"
    cetakData(infoMsg)
    
    pbar = Progress("[INFO] testing query -> ")
    query = getQuery(target.URL)
    
    try:
        for kueri in query:
            kueri = kueri.strip()
            for payload in SQL_PAYLOAD:
                pbar.write(kueri)
                old_url = target.URL
                new_url = old_url.replace(kueri, kueri + payload)
                response = UserAgent.open(new_url)
                htmltext = response.read()
                for errMsg in SQL_ERROR_MESSAGE:
                    if re.search(errMsg, htmltext, re.IGNORECASE):
                        msg = "[INFO] query: {} detected (vuln)"
                        pbar.newline(msg)
                        pbar.finish()
                        
                        raise W3bruteNextStepException
                    
                    pindahBaris()
        
        pbar.finish()
        
    except W3bruteNextStepException:
        infoMsg = "target is detected vulnerable by the SQL injection method"
        
        if not konf.sqliBypass:
            infoMsg += ". use the '--sqli-bypass' option to activate "
            infoMsg += "SQL injection bypass authentication technique."
        
        logger.info(infoMsg)
    
    else:
        warnMsg = "target is not vulnerable to the SQL injection method"
        logger.warning(warnMsg)
