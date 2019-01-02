#!/usr/bin/env python

# Copyright (c) 2018 W3brute Developers.
# See LICENSE for more details.

from lib.core.settings import HOMEPAGE

def check():
    base = "thirdparty"
    modules = (
        "beautifulsoup.beautifulsoup",
        "clientform.clientform",
        "colorama",
        "termcolor.termcolor"
    )
    for name in modules:
        package = base + "." + name
        try:
            __import__(package)
        
        except ImportError, err:
            module = err.message.split()[-1]
            msg = "[CRITICAL] module: %s missing. " % repr(module)
            msg += "please download on %s" % HOMEPAGE
            exit(msg)
        
        except KeyboardInterrupt:
            msg = "[ERROR] user aborted"
            exit(msg)
