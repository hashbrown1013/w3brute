#!/usr/bin/env python

# Copyright (c) 2018 W3brute Developers.
# See LICENSE for more details. 

import os
import platform
import re
import sys
import time

sys.dont_write_bytecode = True

try:
    __import__("lib.utils.check")
except ImportError:
    msg = "[!] wrong installation detected (missing modules). "
    msg += "visit 'https://github.com/aprilahijriyan/w3brute#installation' "
    msg += "for more details."
    exit(msg)

try:
    from lib.controller.start import init
    from lib.controller.start import initOptions
    from lib.controller.target import getTarget
    from lib.core.common import banner
    from lib.core.common import completeUrl
    from lib.core.common import cetakData
    from lib.core.common import clearLine
    from lib.core.common import clearData
    from lib.core.common import completeUrl
    from lib.core.common import disableVerifySslCert
    from lib.core.common import getTerminalSize
    from lib.core.common import getErrorMessage
    from lib.core.data import konf
    from lib.core.data import target
    from lib.core.exception import W3bruteSkipTargetException
    from lib.core.exception import W3bruteQuitException
    from lib.core.log import createLogger
    from lib.core.paths import addBasePath
    from lib.core.settings import VERSION
    from lib.core.settings import IS_WIN
    from lib.parse.cmdline import cmdLineParser

except KeyboardInterrupt:
    msg = "[ERROR] user aborted"
    exit(msg)

def setBasePath():
    """
    mengatur base path
    ini digunakan untuk membantu mencari
    data yang ada di folder `data` w3brute.
    """
    
    path = os.path.dirname(__file__)
    addBasePath(path)

def main():
    """
    fungsi main untuk menjalankan w3brute di terminal
    """
    
    setBasePath()
    disableVerifySslCert()
    createLogger()
    
    try:
        banner()
        options = cmdLineParser() # mendapatkan nilai opsi.
        initOptions(options) # menerapkan nilai opsi ke data konfigurasi.
        
        msg = "\n[*] starting at %s\n\n" % time.strftime("%X")
        cetakData(msg)
        
        # mendapatkan daftar target.
        targetList = getTarget()
        
        for (i, url) in enumerate(targetList):
            i += 1
            
            url = url.strip()
            url = completeUrl(url)
            target.URL = str(url)
            
            infoMsg = "[INFO] #%d url: %s\n" % (i, url)
            cetakData(infoMsg)
            
            try: # menjalankan program
                init()
            
            except W3bruteSkipTargetException:
                clearLine()
                
                if not konf.selesai:
                    infoMsg = "[INFO] skipping target %s\n" % repr(str(url))
                    cetakData(infoMsg)
                else:
                    del konf.selesai
            
            # hapus data target sebelumnya.
            clearData() 
    
    except SystemExit:
        konf.lewat = True
    
    except KeyboardInterrupt:
        errMsg = "user aborted"
        logger.error(errMsg)
    
    except W3bruteQuitException:
        pass
    
    except Exception:
        clearLine()
        
        warnMsg = "something out of control happens.\n"
        warnMsg += ("=" * getTerminalSize()[0]) + "\n"
        warnMsg += "Running version: %s\n" % VERSION
        warnMsg += "Python version: %s\n" % sys.version.split()[0]
        warnMsg += "Operating system: %s\n" % platform.platform()
        warnMsg += "Command line: %s\n" % re.sub(r".+?w3brute.py\b", "w3brute.py", " ".join(sys.argv))
        warnMsg += "=" * getTerminalSize()[0]
        logger.warning(warnMsg)
        
        errMsg = getErrorMessage()
        logger.error(errMsg)
    
    finally:
        if not konf.lewat:
            msg = "\n[-] shutting down at %s\n\n" % time.strftime("%X")
            cetakData(msg)
        
        if IS_WIN:
            msg = "\n[#] press enter to continue... "
            cetakData(msg)
            raw_input()

if __name__ == "__main__":
    main()