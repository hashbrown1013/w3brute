#!/usr/bin/env python

# Copyright (c) 2018 W3brute Developers.
# See LICENSE for more details.

import optparse

from lib.core.common import getTerminalSize

class PrettyHelpFormatter(optparse.IndentedHelpFormatter):
    """
    NOTE: formatter optparse ini berasal dari pip._internal.baseparser.py
    """
    
    def __init__(self, *args, **kwargs):
        kwargs["max_help_position"] = 35
        kwargs["indent_increment"] = 2
        kwargs["width"] = getTerminalSize()[0] - 2
        
        optparse.IndentedHelpFormatter.__init__(self, *args, **kwargs)
    
    def format_option_strings(self, option, format=" <%s>", separator=", "):
        opts = []
        
        if option._short_opts:
            opts.append(option._short_opts[0])
        
        if option._long_opts:
            opts.append(option._long_opts[0])
        
        if len(opts) > 1:
            opts.insert(1, separator)
        
        if option.takes_value():
            metavar = option.metavar or option.dest.lower()
            metavar = format % metavar
            opts.append(metavar)
        
        return "".join(opts)
