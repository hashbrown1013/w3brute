#!/usr/bin/env python

# Copyright (c) 2018 W3brute Developers.
# See LICENSE for more details.

import io
import re

from lib.core.common import cetakData
from lib.core.data import auth
from lib.core.data import html
from lib.core.data import konf
from lib.core.exception import W3bruteSkipParsingFormException
from lib.core.exception import W3bruteSkipTargetException
from lib.core.pydict import PyDict
from thirdparty.beautifulsoup.beautifulsoup import BeautifulSoup
from thirdparty.clientform.clientform import ParseResponse as ParseForm

class ParsePage(object):
    """
    menguraikan html
    """
    
    def __init__(self, response):
        htmltext = response.read()
        source = io.BytesIO(htmltext)
        source.geturl = response.geturl
        self.forms = ParseForm(source)
        self.soup = BeautifulSoup(htmltext)
    
    @property
    def title(self):
        """
        :return: judul halaman
        """
        
        elem = self.soup.find("title")
        return str(elem.text)
    
    def getValidForms(self):
        """
        fungsi ini untuk mendapatkan form 
        yang menuju ke dashboard website
        """
        
        if auth.IS_AUTHORIZATION:
            # skip...
            return;
        
        infoMsg = "[INFO] try searching for form that goes to the website dashboard...\n"
        cetakData(infoMsg)
        
        try:
            for form in self.forms:
                input_controls = form.controls
                for input_elem in input_controls:
                    input_type = input_elem.type
                    # jika input type 'password' ditemukan
                    # itu berarti form tersebut menuju ke
                    # dashboard website.
                    if input_type == "password":
                        html.form = form
                        html.soup = self.soup.find("form", attrs=form.attrs)
                        
                        raise W3bruteSkipParsingFormException
            
        except W3bruteSkipParsingFormException:
            infoMsg = "form that goes to the website dashboard is found"
            logger.info(infoMsg)
        
        else:
            criMsg = "form that goes to the website dashboard is not found. "
            
            if not konf.adminScanner:
                criMsg += "try using the '--admin' option to help you "
                criMsg += "find the admin login page."
            
            logger.critical(criMsg)
            raise W3bruteSkipTargetException
    
    def getTipeAutentikasi(self):
        """
        mendapatkan tipe autentikasi target
        """
        
        infoMsg = "[INFO] detecting target authentication type...\n"
        cetakData(infoMsg)
        
        if auth.IS_AUTHORIZATION:
            infoMsg = "authentication type: %s Authorization" % repr(auth.type.capitalize())
            logger.info(infoMsg)
            
            return;
        
        soup = html.soup
        
        if soup.find("input", type="text"):
            if re.search("(?i)email", str(soup)):
                auth_type = "email"
                auth.IS_EMAIL_AUTH = True
            else:
                auth_type = "standard"
                auth.IS_STANDARD_AUTH = True
        
        elif soup.find("input", type="email"):
            auth_type = "email"
            auth.IS_EMAIL_AUTH = True
        
        else:
            infoMsg = "page title %s" % repr(self.title)
            logger.info(infoMsg)
            
            auth_type = "web shell"
            auth.IS_WEBSHELL_AUTH = True
        
        infoMsg = "authentication type: %s" % repr(auth_type)
        logger.info(infoMsg)
    
    def getParameterForm(self):
        if auth.IS_AUTHORIZATION:
            # skip lagi...
            return;
        
        infoMsg = "[INFO] find parameter(s)...\n"
        cetakData(infoMsg)
        
        soup = html.soup
        html.field = PyDict()
        
        if auth.IS_WEBSHELL_AUTH is None:
            input_elem = soup.find("input", type="text") \
                or soup.find("input", type="email")
            
            if not input_elem.has_key("name"):
                errMsg = "parameter(s) not found in %s" % repr(str(input_elem))
                logger.error(errMsg)
                
                raise W3bruteSkipTargetException
            
            html.field.username = input_elem.get("name")
        
        input_elem = soup.find("input", type="password")
        
        if not input_elem.has_key("name"):
            errMsg = "parameter(s) not found in %s" % repr(str(input_elem))
            logger.error(errMsg)
            
            raise W3bruteSkipTargetException
        
        html.field.password = input_elem.get("name")
