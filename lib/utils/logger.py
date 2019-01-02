#!/usr/bin/env python

# Copyright (c) 2018 W3brute Developers.
# See LICENSE for more details.

from __future__ import absolute_import

import logging
import os

from lib.core.common import getLevelName
from lib.core.common import getLevelColor
from lib.core.common import formatMessage
from lib.core.data import konf
from lib.core.settings import IS_WIN
from thirdparty.colorama import AnsiToWin32

class ColorizedStreamHandler(logging.StreamHandler):
    def __init__(self, stream):
        logging.StreamHandler.__init__(self, stream)
        
        if IS_WIN:
           stream = AnsiToWin32(stream)
        
        self.stream = stream 
        # untuk :func: cetakData()
        konf.colored = self.colored
    
    def colored(self):
        """
        cek jika pesan bisa di warnai
        """
        
        if not konf.noColor:
            _ = self.stream
            if isinstance(_, AnsiToWin32):
                _ = _.wrapped
            
            if hasattr(_, "isatty") and _.isatty():
                return True
            
            if os.getenv("TERM", "").lower() == "ansi":
                return True
        
        return False
    
    def emit(self, record):
        """
        cetak pesan
        """
        
        try:
            message = self.format(record) + "\n"
            self.stream.write(message)
            
            if hasattr(self.stream, "flush"):
                self.stream.flush()
        
        except (SystemExit, KeyboardInterrupt):
            raise
        except IOError:
            pass
        except:
            self.handleError(record)
    
    def mesgColored(self, msg):
        """
        mewarnai pesan
        """
        
        if self.colored():
            levelname = getLevelName(msg)
            color = getLevelColor(levelname, bold=True)
            msg = formatMessage(msg, levelname, color)
        
        return msg
    
    def format(self, record):
        """
        format pesan
        """
        
        msg = logging.StreamHandler.format(self, record)
        return self.mesgColored(msg)
