#!/usr/bin/env python

# Copyright (c) 2018 W3brute Developers.
# See LICENSE for more details.

import cookielib
import urllib
import urllib2

from lib.core.data import auth
from lib.core.data import konf
from lib.core.exception import W3bruteRedirectException

class DisableRedirect(urllib2.HTTPRedirectHandler):
    """
    tidak mengijinkan redirect 
    ini digunakan untuk proses verifikasi
    """
    
    def redirect_request(self, *_):
        raise W3bruteRedirectException 

def getAuthHandler():
    """
    reference: https://docs.python.org/2/howto/urllib2.html
    """
    
    passw_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    if auth.type == "digest":
        authHandler = urllib2.HTTPDigestAuthHandler(passw_mgr)
    else:
        authHandler = urllib2.HTTPBasicAuthHandler(passw_mgr)
    
    return authHandler

def getProxyHandler():
    """
    reference: http://www.learntosolveit.com/python/web_urllib2_proxy_auth.html
    """
    handlers = []
    proxyDict = getProxy() if konf.proxy else urllib.getproxies() 
    proxyHandler = urllib2.ProxyHandler(proxyDict)
    handlers.append(proxyHandler)
    if "@" in " ".join(proxyDict.values()):
        handlers.append(urllib2.HTTPBasicAuthHandler())
        handlers.append(urllib2.HTTPHandler)
    
    return handlers

def getCookieHandler():
    cookieJar = cookielib.CookieJar()
    cookieHandler = urllib2.HTTPCookieProcessor(cookieJar)
    return cookieHandler