#!/usr/bin/env python

# Copyright (c) 2018 W3brute Developers.
# See LICENSE for more details.

import errno
import time
import urllib2

from lib.core.common import clearLine
from lib.core.data import konf
from lib.core.data import target
from lib.core.exception import W3bruteSkipTargetException
from lib.core.exception import W3bruteQuitException

def checkErrorCode(response):
    errcode, message = response
    if errcode == errno.ENOENT:
        errMsg = "internet connection is not detected"
        logger.error(errMsg)
        
        raise W3bruteQuitException
    
    elif errcode == errno.E2BIG:
        errMsg = "host %s doest not exist" % repr(target.HOST)
        logger.error(errMsg)
        
        raise W3bruteSkipTargetException
    
    elif errcode == errno.ETIMEDOUT:
        warnMsg = "w3brute get a response '%s' (%d). " % (message, errcode)
        warnMsg += "try to re-connect..."
        logger.warning(warnMsg)
        
        tidur = False
        for i in xrange(konf.retries):
            if not tidur:
                # tidur sebentar dan mencoba
                # untuk terhubung kembali.
                time.sleep(konf.delay)
                tidur = True
                
                try:
                    return urllib2.urlopen(req)
                except:
                    # tidur lagi, habis begadang :)
                    time.sleep(konf.delay) 
            
            criMsg = "failed to connect to server. "
            criMsg += "please check your internet connection."
            logger.critical(criMsg)
            
            raise W3bruteQuitException
            
        else:
            # FIXME: how to fix this?
            if "Interrupted" in message:
                clearLine()
                logger.critical(message)
                raise W3bruteSkipTargetException
            
            errMsg = "your internet connection has a problem. "
            errMsg += "connection response '%s' (%d)" % (message, errcode)
            logger.error(errMsg)
            
            raise W3bruteQuitException
