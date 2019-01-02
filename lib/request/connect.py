#!/usr/bin/env python

# Copyright (c) 2018 W3brute Developers.
# See LICENSE for more details.

import urllib2

from lib.core.common import clearLine
from lib.core.common import prepareRequest
from lib.core.common import useProxy
from lib.core.data import konf
from lib.request.error import checkErrorCode
from lib.request.handler import getAuthHandler
from lib.request.handler import getProxyHandler
from lib.request.handler import getCookieHandler
from lib.request.handler import DisableRedirect

class UserAgent(object):
    """
    simpel URL opener
    """
     
    @staticmethod
    def open(url, authCred=None, allow_redirects=True):
        req = prepareRequest(url)
        handlers = []
        
        if isinstance(authCred, tuple):
            authHandler = getAuthHandler()
            authHandler.add_password(None, req.get_full_url(), *authCred) 
            handlers.append(authHandler)
        
        if useProxy():
            proxyHandler = getProxyHandler()
            handlers.extend(proxyHandler)
            
        cookieHandler = getCookieHandler()
        handlers.append(cookieHandler)
        
        if not allow_redirects:
            disableRedirect = DisableRedirect()
            handlers.append(disableRedirect)
        
        opener = urllib2.build_opener(*handlers)
        urllib2.install_opener(opener)
        
        try:
            return urllib2.urlopen(req)
        except urllib2.HTTPError, ex:
            return ex
        except urllib2.URLError, ex:
            return checkErrorCode(ex.reason)
