#!/usr/bin/env python

# Copyright (c) 2018 W3brute Developers.
# See LICENSE for more details.

import signal

from lib.core.common import cetakData
from lib.core.data import konf
from lib.core.exception import W3bruteNextStepException
from lib.core.exception import W3bruteSkipTargetException
from lib.core.exception import W3bruteStopBruteForceException
from lib.core.exception import W3bruteQuitException

class InterruptHandler(object):
    """
    fungsi kelas ini untuk menghandle sinyal interrupt
    dari CTRL - C dan CTRL - Z secara otomatis
    reference: https://unix.stackexchange.com/questions/256799/ctrlc-and-ctrlz-to-interrupt-suspend-jobs 
    """
    
    def __init__(self):
        self.setupHandler()
    
    def setupHandler(self, handler=None):
        """
        mengatur interrupt handler
        """
        
        if handler is None:
            handler = self.defaultHandler
        
        self.handler = handler
        signal.signal(signal.SIGINT, handler) # signal.SIGINT = sinyal CTRL - C
        signal.signal(signal.SIGTSTP, handler) # signal.SIGTSTP = sinyal CTRL - Z
    
    def defaultHandler(self, signum, frame):
        """
        interrupt handler
        """
        
        if isinstance(konf.handleInterrupt, bool) and not konf.handleInterrupt:
            raise W3bruteNextStepException
        
        if not hasattr(self, "sudah"):
            warnMsg = "interrupt detected"
            logger.warning(warnMsg)
            self.sudah = True
        
        try:
            msg = "[ASK] what do you want? [(C)ontinue (default) / (s)kip target / (q)uit]: "
            jawaban = raw_input(msg).lower() or "c"
            if jawaban.startswith("c"):
                pass
            
            elif jawaban.startswith("s"):
                raise KeyboardInterrupt
            
            elif jawaban.startswith("q"):
                errMsg = "[ERROR] user quit\n"
                cetakData(errMsg)
                
                if konf.bruteSession:
                    raise W3bruteStopBruteForceException
                 
                raise W3bruteQuitException
            
            else:
                warnMsg = "[WARNING] invalid choice: %s\n" % repr(jawaban)
                cetakData(warnMsg)
                raise W3bruteSkipTargetException
        
        except KeyboardInterrupt:
            errMsg = "[ERROR] user stopped\n"
            cetakData(errMsg)
            
            if konf.bruteSession:
                raise W3bruteStopBruteForceException
            
            raise W3bruteSkipTargetException
        
        except RuntimeError:
            errMsg = "user aborted"
            logger.error(errMsg)
            raise W3bruteQuitException
