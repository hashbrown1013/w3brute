#!/usr/bin/env python

# Copyright (c) 2018 W3brute Developers.
# See LICENSE for more details.

from __future__ import absolute_import

import itertools
import random
import re
import signal
import textwrap

from lib.core.common import cetakData
from lib.core.common import clearLine
from lib.core.common import getLevelName
from lib.core.common import getTerminalSize
from lib.core.common import ignoreInterrupt
from lib.core.data import konf
from lib.core.settings import SPINNER_CHAR
from lib.utils.sigint import InterruptHandler
from thirdparty.colorama import Fore
from thirdparty.colorama import Style
from thirdparty.termcolor.termcolor import colored as warnai

class Progress(InterruptHandler):
    """
    simpel text progress
    """
    
    def __init__(self, message=None):
        InterruptHandler.__init__(self)
        
        self.setupHandler(self.newHandler)
        
        self.message = message
        self.curmesg = None
        self.width = getTerminalSize()[0]
        
        # menambahkan handler untuk menghandle jika ukuran terminal berubah
        # reference: https://stackoverflow.com/questions/16941885/want-to-resize-terminal-windows-in-python-working-but-not-quite-right 
        signal.signal(signal.SIGWINCH, self.handleResize)
    
    def write(self, msg):
        """ 
        cetak data ke terminal
        """
        
        clearLine()
        
        # simpan pesan, yang nantinya akan digunakan oleh
        # fungsi newline()
        self.curmesg = msg
        
        msg = self.message + msg
        if len(msg) >= self.width:
            # untuk lebar terminal kurang dari 51
            # pesan akan secara otomatis di pendekan.
            if self.width <= 50:
                if not konf.disableWrap:
                    msg = textwrap.wrap(msg, self.width)[0][:-4] + "..."
                else:
                    konf.garisBaru = True
            else:
                konf.garisBaru = True
        
        msg = msg.ljust(self.width)
        
        if konf.colored():
            msg = Fore.GREEN + msg + Style.RESET_ALL
        
        cetakData(msg)
    
    def newline(self, msg):
        """
        mencetak text dan pindah ke garis baru
        """
        
        clearLine()
        
        if konf.colored():
            color = Fore.LIGHTGREEN_EX
            bold = Fore.LIGHTWHITE_EX
            reset = Style.RESET_ALL
            levelname = getLevelName(msg)
            msg = bold + msg.replace(levelname, color + levelname + reset)
            text = re.search("\((.+)\)", msg).group(1)
            msg = msg.replace(text, color + text + reset)
            
            if ":" not in self.curmesg:
                self.curmesg = warnai(self.curmesg, "green", attrs=["bold", "underline"])
            else:
                usr, psw = self.curmesg.split(" : ")
                self.curmesg = warnai(usr, "green", attrs=["bold", "underline"]) + " : " + warnai(psw, "green", attrs=["bold", "underline"])
        
        msg = msg.format(self.curmesg)
        msg += "\n"
        
        cetakData(msg)
    
    def finish(self):
        """ 
        atur ulang sinyal
        """
        
        signal.signal(signal.SIGWINCH, signal.SIG_DFL)
    
    def handleResize(self, signum, frame):
        """
        update ukuran terminal
        """
        
        self.width = getTerminalSize()[0]
    
    def newHandler(self, signum, frame):
        """
        interrupt handler untuk menghandle interupsi
        yang sedang 'menggunakan text progress' ini.
        """
        
        clearLine()
        self.finish()
        self.defaultHandler(signum, frame)
        # reference: https://stackoverflow.com/questions/16941885/want-to-resize-terminal-windows-in-python-working-but-not-quite-right 
        signal.signal(signal.SIGWINCH, self.handleResize)

class Spinner(object):
    """
    progress spinner
    """
    
    def __init__(self, message, maxval=None, suffix="%(percent)d%%"):
        self.message = message
        self.marker = itertools.cycle(SPINNER_CHAR)
        self.curlen = 0
        self.curval = 0
        self.maxval = maxval or 100
        self.suffix = suffix
        self.width = getTerminalSize()[0]
        self.curmesg = None
        self._show_proses_lengkap = True
        
        ignoreInterrupt()
        
        # menambahkan handler untuk menghandle jika ukuran terminal berubah
        # reference: https://stackoverflow.com/questions/16941885/want-to-resize-terminal-windows-in-python-working-but-not-quite-right 
        signal.signal(signal.SIGWINCH, self.handleResize)
        
        cetakData(message)
    
    def __getitem__(self, name):
        """
        memberikan nilai item
        """
        
        return getattr(self, name, "")
    
    @property
    def percent(self):
        """
        persentase progress
        """
        
        return (self.curval * 100) / self.maxval
    
    def write(self, msg):
        """
        cetak karakter/pesan ke terminal
        """
        
        backspace = "\b" * self.curlen
        self.curlen = max(self.curlen, len(msg))
        if konf.colored():
            spin = msg[-1]
            msg = msg[:-1] + random.choice(Fore.__dict__.values()) + spin
        
        msg = backspace + msg.ljust(self.curlen)
        cetakData(msg)
    
    def show_progress(self):
        """
        menampilkan spinner progress
        """
        
        # update value
        self.curval += 1
        if not self._show_proses_lengkap:
            self.suffix = "%(percent)d%%"
        
        suffix = self.suffix % self
        char = self.marker.next()
        msg = "%(suffix)s %(spin)s" % dict(suffix=suffix, spin=char)
        self.curmesg = msg
        self.write(msg)
        self.checkLength()
    
    def checkLength(self):
        """
        memeriksa panjang pesan
        """
        
        if len(self.message + self.curmesg) >= self.width:
            self._show_proses_lengkap = False
            self.curlen = 0
            if not hasattr(self, "_sudah_di_perbaiki"):
                self._sudah_di_perbaiki = True
                clearLine()
            
            cetakData(self.message)
    
    def handleResize(self, signum, frame):
        """
        update ukuran terminal
        """
        
        self.width = getTerminalSize()[0]
    
    def resetSignal(self):
        """ 
        atur ulang sinyal handler ke default 
        """
        
        signal.signal(signal.SIGWINCH, signal.SIG_DFL) 
    
    def done(self, msg=""):
        """ 
        cetak pesan selesai
        """
        
        clearLine()
        cetakData(msg)
        
        if msg: # jika msg bukan null
            # pindah ke garis baru.
            cetakData("\n")
        
        # aktifkan kembali interrupt handler
        ignoreInterrupt(False)
        self.resetSignal() 
