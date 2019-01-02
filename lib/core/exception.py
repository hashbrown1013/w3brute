#!/usr/bin/env python

# Copyright (c) 2018 W3brute Developers.
# See LICENSE for more details.

class W3bruteBaseException(Exception):
    pass

class W3bruteNextStepException(W3bruteBaseException):
    pass

class W3bruteRedirectException(W3bruteBaseException):
    pass

class W3bruteSkipParsingFormException(W3bruteBaseException):
    pass

class W3bruteSkipTargetException(W3bruteBaseException):
    pass

class W3bruteStopBruteForceException(W3bruteBaseException):
    pass

class W3bruteQuitException(W3bruteBaseException):
    pass
