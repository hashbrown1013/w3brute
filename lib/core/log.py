#!/usr/bin/env python

# Copyright (c) 2018 W3brute Developers.
# See LICENSE for more details.

import logging
import sys

from lib.core.common import installBuiltin
from lib.utils.logger import ColorizedStreamHandler

def createLogger():
    """
    pengaturan logger untuk mencetak text ke terminal
    """
    
    logger = logging.Logger("w3bruteLog")
    formatter = logging.Formatter("\r[%(levelname)s] %(message)s")
    logger_handler = ColorizedStreamHandler(sys.stdout)
    logger_handler.setFormatter(formatter)
    logger.addHandler(logger_handler)
    logger.setLevel(logging.INFO)
    
    installBuiltin("logger", logger)
    installBuiltin("stream", logger_handler.stream)
