#!/usr/bin/env python

# Copyright (c) 2018 W3brute Developers.
# See LICENSE for more details.

from __future__ import absolute_import

import os
import re
import urllib
import urlparse

from lib.core.common import cetakData
from lib.core.common import createList
from lib.core.common import createFileObject
from lib.core.common import getErrorMessage
from lib.core.common import getPage
from lib.core.common import getSchemeAuth
from lib.core.data import auth
from lib.core.data import konf
from lib.core.data import target
from lib.core.exception import W3bruteNextStepException
from lib.core.exception import W3bruteSkipTargetException
from lib.core.exception import W3bruteQuitException
from lib.parse.page import ParsePage
from lib.request.connect import UserAgent
from lib.utils.text import Spinner
from thirdparty.beautifulsoup.beautifulsoup import BeautifulSoup

def checkTarget():
    """
    memeriksa target jika support di bruteforce
    """
    
    url = target.URL
    target.HOST = urlparse.urlparse(url).netloc
    
    infoMsg = "[INFO] check the target if the target has the potential to attack...\n"
    cetakData(infoMsg)
    
    response = UserAgent.open(url)
    code = response.code
      
    if code == 401:
        auth.IS_AUTHORIZATION = True
    
    elif code == 200:
        infoMsg = "[INFO] search form...\n"
        cetakData(infoMsg)
    
    else:
        errMsg = "[ERROR] HTTP error code %d (%s)\n" % (code, repr(response.reason))
        cetakData(errMsg)
        raise W3bruteSkipTargetException
    
    target.PAGE = getPage(response.geturl())
    parsed = ParsePage(response)
    
    if len(parsed.forms) > 0 or code == 401:
        if code != 401:
            infoMsg = "detected target has %d forms" % len(parsed.forms)
            logger.info(infoMsg)
        else:
            headers = response.info()
            auth.type = getSchemeAuth(headers)
        
        return parsed
    
    else:
        criMsg = "form not found. "
        
        if not konf.adminScanner:
            criMsg += "try using the '--admin' option to help you "
            criMsg += "find the admin login page."
        
        logger.critical(criMsg)
        raise W3bruteSkipTargetException

def getTarget():
    """
    mendapatkan daftar target
    """
    
    targetList = None
    
    if not konf.googleSearch:
        targetList = createList(*konf.target)
        
        infoMsg = "[INFO] total target: %d\n" % len(targetList)
        cetakData(infoMsg)
    
    else:
        try:
            targetList = searchGoogle()
        
        except W3bruteNextStepException:
            raise W3bruteQuitException
        
        except Exception:
            errMsg = "what happened?. %s" % getErrorMessage()
            logger.error(errMsg)
            raise W3bruteQuitException 
        
        if targetList is None:
            warnMsg = "[WARNING] unsuccessful in getting search results with dork %s. " % repr(konf.googleDork)
            warnMsg += "try using another dork (e.g. 'inurl:/admin/index.php')\n"
            cetakData(warnMsg) 
            
            raise W3bruteQuitException
        
        infoMsg = "google search results get %d target(s)" % len(targetList)
        logger.info(infoMsg)
        
        charunik = os.urandom(4).encode("hex")
        filename = "result-dorking-w3brute-" + charunik
        format = "txt"
        fp = createFileObject(filename, format, False)
        
        maxval = len(targetList)
        spin = Spinner("[INFO] saving results... ", maxval=maxval)
        
        try:
            for url in targetList:
                fp.write(url + "\n")
                spin.show_progress()
        
        except W3bruteNextStepException:
            pass
        
        fp.close()
        spin.done()
        
        infoMsg = "dorking results are stored in %s" % repr(fp.name)
        logger.info(infoMsg)
    
    return targetList

def searchGoogle():
    infoMsg = "[INFO] google dorking is running, please wait...\n"
    cetakData(infoMsg)
    
    dork, page = konf.target
    page = page if page > 1 else 1
    # atur kembali
    konf.googleDork = dork
    
    data = {
        "q": dork,
        "num": 100,
        "hl": "en",
        "complete": 0,
        "safe": "off",
        "filter": 0,
        "btnG": "search",
        "start": page
    }
    
    url = "https://www.google.com/search?" + urllib.urlencode(data)
    response = UserAgent.open(url)
    htmltext = response.read()
    
    if re.search("(?i)captcha", htmltext):
        criMsg = "can't get dorking results. "
        criMsg += "captcha challenge detected"
        
        logger.critical(criMsg)
        raise W3bruteNextStepException
    
    soup = BeautifulSoup(htmltext)
    h3tags = soup.findAll("h3", attrs={"class":"r"})
    urls = [urlparse.parse_qsl(urlparse.urlsplit(tag.a["href"]).query)[0][1] for tag in h3tags]
    
    return urls or None
