#!/usr/bin/env python

# Copyright (c) 2018 W3brute Developers.
# See LICENSE for more details.

from __future__ import absolute_import

import __builtin__

import codecs
import logging
import os
import random
import re
import shutil
import socket
import sqlite3
import ssl
import struct
import sys
import traceback
import urllib
import urllib2
import urlparse
import zipfile

from lib.core.data import auth
from lib.core.data import defaults
from lib.core.data import html
from lib.core.data import konf
from lib.core.data import target
from lib.core.data import status
from lib.core.exception import W3bruteNextStepException
from lib.core.exception import W3bruteStopBruteForceException
from lib.core.exception import W3bruteSkipTargetException
from lib.core.exception import W3bruteQuitException
from lib.core.settings import BANNER
from lib.core.settings import VERSION_STRING
from lib.core.settings import HOMEPAGE
from lib.core.settings import URL_SCHEMES
from lib.core.settings import DEFAULT_URL_SCHEME
from lib.core.settings import ZIP_PATTERN
from lib.core.settings import DB_PATTERN
from lib.core.settings import JAVASCRIPT_ACTION_PATTERN
from thirdparty.colorama import ansi
from thirdparty.colorama import Fore
from thirdparty.colorama import init as coloramainit
from thirdparty.colorama import Style
from thirdparty.termcolor.termcolor import colored as warnai

def disableVerifySslCert():
    """
    reference: https://stackoverflow.com/questions/27835619/urllib-and-ssl-certificate-verify-failed-error
    """
    
    try: 
        ssl._create_default_https_context = ssl._create_unverified_context
    except AttributeError:
        pass

def setSocketTimeout():
    """
    mengatur timeout
    """
    
    socket.setdefaulttimeout(konf.timeout)

def getUserAgentHeader():
    """
    mengatur nilai HTTP header `User-Agent`
    """
    
    return {"User-Agent": konf.agent}

def prepareRequest(url):
    """
    persiapan urllib2.Request
    """
    
    setSocketTimeout()
    headers = getUserAgentHeader()
    
    if isinstance(url, urllib2.Request):
        url.headers = headers
        req = url
    else:
        req = urllib2.Request(url, headers=headers)
    
    return req

def useProxy():
    """
    memeriksa jika menggunakan proxy
    """
    
    return bool(konf.proxy or urllib.getproxies())

def banner():
    """
    menampilkan logo w3brute
    """
    
    coloramainit()
    
    ac = [Fore.GREEN, Fore.LIGHTGREEN_EX]
    bc = [Fore.RED, ansi.code_to_chars("41")]
    cc = {
        "g": ac,
        ".": bc
    }
    
    _ = BANNER
    for k, v in cc.items():
        rc = random.choice(v)
        _ = _.replace(k, rc + k + Style.RESET_ALL)
    
    old = re.findall(r": (.*) ]", _)[0]
    new = Fore.LIGHTRED_EX + old.replace(", ", Style.RESET_ALL + ", " + Fore.LIGHTBLUE_EX) + Style.RESET_ALL
    _ = _.replace(old, new)
    
    data = {}
    data["VERSION"] = Fore.YELLOW + VERSION_STRING + Style.RESET_ALL
    data["HOMEPAGE"] = warnai(HOMEPAGE, "white", attrs=["underline"])
    
    cetakData(_ % data)

def installBuiltin(name, func):
    """
    untuk menambahkan fungsi (built-in)
    baru pada python.
    """
    
    setattr(__builtin__, name, func)

def uninstallBuiltin(name):
    """
    menghapus fungsi (built-in)
    """
    
    delattr(__builtin__, name)

def randomHexColor():
    """
    warna acak untuk hasil file format (.html)
    """
    
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    color = "#%x%x%x" % (r, g, b)
    return color

def parseSlice(obj):
    """
    menguraikan slice syntax (string)
    """
    
    _ = None
    
    if obj is None:
        # .
        return slice(0, None)
    
    if obj.startswith(":"):
        obj = obj[1:]
    
    if obj.endswith(":"):
        obj = obj[:-1]
    
    if ":" in obj:
        _ = []
        val = obj.split(":")
        
        for v in val:
            try: int(v) # slice object harus tipe integer. 
            except: pass
            else: _.append(int(v))
        
        if len(_) == 0:
            _ = [0, None]
        
        elif len(_) == 1:
            _ = [_[0], None]
        
        elif len(_) == 2:
            start = _[0]
            stop = _[1] or None
            _ = [start, stop]
        
        elif len(_) >= 3:
            _ = _[0:3]
    
    else:
        start = 0
        try: int(obj)
        except: pass
        else: start = int(obj)
        
        _ = [start, None]
    
    return slice(*_)

def stringToList(s, sep=","):
    """
    membuat tipe data string atau (file) ke tipe data list
    """
    
    if "\r" in s:
        # * newline style:
        if "\n" in s:
            # Windows
            s = s.replace("\r", "")
        else:
            # Mac OS
            s = s.split("\r")
            return s
    
    if "\n" in s:
        # linux
        _ = s.splitlines()
    
    elif sep in s:
        if s.startswith(sep):
            s = s.lstrip(sep)
        
        if s.endswith(sep):
            s = s.rstrip(sep)
        
        if sep in s:
            _ = s.split(sep)
        else:
            _ = [s]
    
    else:
        _ = [s]
    
    return _

def openFile(f):
    """
    membuka file
    """
    
    try:
       with codecs.open(f, mode="r", encoding=sys.getfilesystemencoding()) as f:
           return f.read()
    
    except Exception:
        errMsg = getErrorMessage()
        logger.critical(errMsg)
        raise W3bruteQuitException

def is_zipfile(object_):
    """
    mencocokan syntax (jika anda menggunakan file zip)
    
    :rtype: boolean
    
    """
    
    if re.search(ZIP_PATTERN, object_):
        return True
    
    return False

def parseZipSyntax(object_):
    """ menguraikan syntax untuk file zip
    
    :syntax: <filepath><;filename><[:password]>
    
    :filepath: (e.g. /path/to/file.zip)
    :filename: (e.g. usernames.txt)
    :password: (e.g. mypass) (optional)
    
    :example: /path/to/file.zip;usernames.txt:mypass
    
    :rtype: tuple
    
    """
    
    filepath = filename = password = None
    if ";" in object_:
        filepath, filename = object_.split(";", 1)
    
    if filename is not None:
        if ":" in filename:
            filename, password = filename.split(":", 1)
    
    return filepath, filename, password

def openZip(filepath, filename, password=None):
    """
    membuka file didalam file zip
    
    :param filepath: path file zip
    :param filename: nama file yang ada di dalam file zip
    :param password: password file (optional)
    
    :rtype: string
    
    """
    
    zip_ = None
    
    try:
        zip_ = zipfile.ZipFile(filepath)
    
    except IOError, err:
        errMsg = err[1].lower() + ": " + repr(filepath)
        logger.error(errMsg)
        raise W3bruteQuitException
    
    except zipfile.BadZipFile, err:
        errMsg = "".join(err).lower()
        logger.error(errMsg)
        raise W3bruteQuitException
    
    members = zip_.namelist()
    if filename not in members:
        criMsg = "file '%s' not found in '%s' file" % (filename, filepath)
        logger.critical(criMsg)
        raise W3bruteQuitException
    
    wordlist = None
    
    try:
        wordlist = zip_.read(filename)
    except RuntimeError, err:
        errMsg = "".join(err).lower()
        if not re.search("password required", errMsg, re.IGNORECASE):
            errMsg += ". what happened?"
            logger.error(errMsg)
            raise W3bruteQuitException
        
        if password:
            infoMsg = "[INFO] opening file %s " % repr(filename)
            infoMsg += "in '%s' with password '%s'\n" % (filepath, password)
            cetakData(infoMsg)
            
            try:
                wordlist = zip_.read(filename, pwd=password)
            except RuntimeError, err:
                errMsg = "%s '%s'" % err.args
                logger.error(errMsg.lower())
                raise W3bruteQuitException
            else:
                infoMsg = "[INFO] password: %s (valid)\n" % repr(password)
                cetakData(infoMsg) 
                return wordlist
        else:
            warnMsg = "[WARNING] %s (press 'CTRL-C' to exit)\n" % errMsg
            cetakData(warnMsg)
        
        ignoreInterrupt()
        
        while True:
            try:
                pwd = raw_input("[#] enter password: ").strip() or None
                if pwd is None:
                    continue
            
            except W3bruteNextStepException:
                errMsg = "[ERROR] user quit\n"
                cetakData(errNsg)
                raise W3bruteQuitException
            
            try:
                wordlist = zip_.read(filename, pwd=pwd)
            
            except RuntimeError:
                errMsg = "wrong password: %s" % repr(pwd)
                logger.error(errMsg)
            
            else:
                infoMsg = "[INFO] password: %s (valid)\n" % repr(pwd)
                cetakData(infoMsg)
                break
    
    ignoreInterrupt(False)
    return wordlist

def is_db(object_):
    """
    regex untuk mengetahui
    jika objek adalah *database*
    
    :rtype: boolean
    
    """
    
    if re.search(DB_PATTERN, object_):
        return True
    
    return False

def parseDbSyntax(object_):
    """
    menguraikan syntax file *database* (web.db)
    
    :rtype: tuple
    
    """
    
    filepath = table_name = column_name = None
    if ">" in object_:
        filepath, table_name = object_.split(">", 1)
    
    if table_name is not None:
        if ";" in table_name:
            table_name, column_name = table_name.split(";", 1)
    
    return filepath, table_name, column_name

def openDb(filepath, table_name, column_name):
    """
    membuka file web.db
    
    :rtype: string
    
    """
    
    conn = sqlite3.connect(filepath)
    conn.text_factory = str
    cur = conn.cursor()
    cur.execute("select %s from %s" % (column_name, table_name))
    data = cur.fetchone()[0]
    return data

def createList(obj, isfile=False):
    """
    cek objek dan convert objek ke list
    """
    
    if os.path.isfile(obj):
        _ = stringToList(openFile(obj))
        return _
    
    elif is_db(obj):
        args = parseDbSyntax(obj)
        _ = stringToList(openDb(*args))
        return _
     
    elif is_zipfile(obj):
        args = parseZipSyntax(obj)
        _ = stringToList(openZip(*args))
        return _
    
    if isfile:
        errMsg = "file %s doest not exists" % repr(os.path.basename(obj))
        logger.error(errMsg)
        
        raise W3bruteQuitException
    
    _ = stringToList(obj)
    return _

# reference: https://stackoverflow.com/questions/566746/how-to-get-linux-console-window-width-in-python 
if hasattr(shutil, 'get_terminal_size'):
    def getTerminalSize():
        """
        return (width, height)
        """
        return tuple(shutil.get_terminal_size())
else:
    def getTerminalSize():
        """
        reference: https://gist.github.com/jtriley/1108174
        return (width, height)
        """
        import platform
        
        current_os = platform.system()
        if current_os in ['Linux', 'Darwin'] or current_os.startswith('CYGWIN'):
            def ioctl_GWINSZ(fd):
                import fcntl
                import termios
                try:
                    cr = struct.unpack_from(
                        'hh',
                        fcntl.ioctl(fd, termios.TIOCGWINSZ, '12345678')
                    )
                except Exception:
                    return None
            
                if cr == (0, 0):
                    return None
                
                return cr
            
            cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
            if not cr:
                try:
                    fd = os.open(os.ctermid(), os.O_RDONLY)
                    cr = ioctl_GWINSZ(fd)
                    os.close(fd)
                except Exception:
                    pass
        
            if not cr:
                cr = (os.getenv('LINES', 40), os.getenv('COLUMNS', 80))
        
            # width, height
            return int(cr[1]), int(cr[0])
        
        elif current_os == "Windows":
            # fix the bug: https://github.com/aprilahijriyan/w3brute/issues/1
            try:
                from ctypes import windll, create_string_buffer
                
                # stdin handle is -10
                # stdout handle is -11
                # stderr handle is -12
                
                h = windll.kernel32.GetStdHandle(-12)
                csbi = create_string_buffer(22)
                res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
                if res:
                    (bufx, bufy, curx, cury, wattr,
                        left, top, right, bottom,
                        maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)

                sizex = right - left + 1
                sizey = bottom - top + 1
                
                return sizex, sizey
            
            except:
                pass
                
                # src: http://stackoverflow.com/questions/263890/how-do-i-find-the-width-height-of-a-terminal-window
                try:
                    import shlex
                    import subprocess
                    
                    cols = int(subprocess.check_output(shlex.split('tput cols')))
                    rows = int(subprocess.check_output(shlex.split('tput lines')))
                    return (cols, rows)
                except:
                    # default
                    return (80, 40)
        
        else:
            # ?
            return (80, 40)


def replaceSlice(object_, start, end, new):
    """
    mengganti karakter sesuai *letak posisi* dari karakter tersebut.
    
    :param object_: objek harus didukung :meth: slicing
    :param start: index (awal) karakter
    :param end: index (akhir) karakter
    :param new: karakter baru untuk pengganti karakter lama
    
    """
    
    try:
        a, c = object_[:start], object_[end:]
    except TypeError, err:
        tobject = err[0].split()[0]
        raise TypeError("%s object is not supported by slicing method" % tobject)
    
    b = type(object_)(new)
    object_ = a + b + c
    return object_

def getLevelName(msg):
    """
    mendapatkan nama (level)
    dari pesan.
    """
    
    match = re.search("\[(.+)\]", msg)
    lv = match.group(1).upper() if match else None
    return lv

def getLevelColor(lv, bold=False):
    """
    mendapatkan warna level
    
    :param bold: jika `True` return warna bold
    
    """
    
    # warna untuk :func: cetakData()
    soft_color = {
        "INFO": Fore.GREEN,
        "ERROR": Fore.RED,
        "WARNING": Fore.YELLOW
    }
    # warna untuk :func: logger
    bold_color = {
        "INFO": Fore.LIGHTGREEN_EX,
        "ERROR": Fore.LIGHTRED_EX,
        "WARNING": Fore.LIGHTYELLOW_EX
    }
    
    if lv == "CRITICAL":
        color = ansi.code_to_chars("41")
    else:
        color = soft_color[lv] if not bold else bold_color[lv]
    
    return color

def formatMessage(msg, lv, color):
    """
    format warna pesan
    """
    
    white = Fore.LIGHTWHITE_EX
    reset = Style.RESET_ALL
    msg = white + msg.replace(lv, color + lv + \
        (reset + white if lv == "CRITICAL" else white)
    )
    
    if lv == "CRITICAL":
        color = Fore.RED
    
    qmsg = []
    for match in re.finditer(r"'(.*?)'", msg):
        if match:
            text = color + "'" + Fore.WHITE + match.group(1) + color + "'"
            qmsg.append((match.start(), match.end(), text))
    
    qmsg.reverse()
    for start, end, text in qmsg:
        msg = replaceSlice(msg, start, end, text)
    
    msg = msg.replace("] ", "] " + color) + reset
    return msg

def clearLine():
    """
    membersihkan line di terminal
    """
    
    line = "\r%s\r" % (" " * getTerminalSize()[0])
    cetakData(line)

def cetakData(msg):
    """
    cetak data tanpa pindah baris secara otomatis
    """
    
    if msg.startswith("[") and konf.colored():
        levelname = getLevelName(msg)
        color = getLevelColor(levelname)
        msg = formatMessage(msg, levelname, color)
        match = re.search("\#(\d+)", msg)
        if match:
            num = "#" + match.group(1)
            msg = msg.replace(num, Fore.LIGHTCYAN_EX + num + color)
    
    try:
        stream.write(msg)
        if hasattr(stream, "flush"):
            stream.flush()
    
    except IOError:
        pass

def getOutputDir():
    """ 
    cek dan memberikan output directory
    """
    
    outdir = konf.outputDir
    if not os.path.exists(outdir):
        try:
            os.mkdir(outdir)
        except OSError, ex:
            if "no space left" in ex.args[1]:
                raise W3bruteQuitException(*ex.args)
            
            warnMsg = "[WARNING] %s %s. use default output directory %s\n" % (ex.args[1], repr(outdir), repr(defaults.outputDir))
            cetakData(warnMsg)
            
            # atur kembali ke default output directory
            # jika directory yang anda masukan tidak valid.
            outdir = konf.outputDir = defaults.outputDir
            if not os.path.exists(outdir):
                os.mkdir(outdir)
    
    if outdir.endswith("/"):
        outdir = outdir.rstrip("/")
    
    return outdir

def createFileObject(filename=None, format=None, buat_target_dir=True):
    """
    membuat file-object untuk membuat file hasil 
    """
    
    basedir = getOutputDir()
    
    if buat_target_dir:
        dirname = "/" + urllib.splitport(target.HOST)[0]
    else:
        dirname = "/dorking"
    
    outdir = basedir + dirname
    if not os.path.exists(outdir):
        try:
            os.mkdir(outdir)
        except OSError, ex:
            if "no space left" in ex.args[1]:
                raise W3bruteQuitException(*ex.args)
            
            warnMsg = "[WARNING] '%s' '%s'. use default output directory '%s'\n" % (ex.args[1], outdir, defaults.outputDir)
            cetakData(warnMsg)
            
            # atur kembali ke default output directory
            # jika directory yang anda masukan tidak valid.
            konf.outputDir = defaults.outputDir
            outdir = getOutputDir()
            outdir = outdir + dirname
            if not os.path.exists(outdir):
                os.mkdir(outdir)
    
    filename = konf.filename if filename is None else filename
    format = konf.fileFormat if format is None else format
    
    fp = outdir + "/" + filename + "." + format
    try:
        fp = open(fp, "w")
    except IOError:
        default_fp = outdir + "/" + defaults.filename + "." + format 
        warnMsg = "can't create %s file. " % repr(fp)
        warnMsg += "use default file result %s" % repr(default_fp)
        logger.warning(warnMsg)
        
        fp = open(default_fp, "w")
    
    return fp

def ignoreInterrupt(value=True):
    """
    mengabaikan interupsi
    """
    
    konf.handleInterrupt = not value

def completeUrl(u):
    """
    menambahkan scheme ke url jika URL tidak memiliki `scheme`
    """
    
    if not u.startswith(URL_SCHEMES):
        u = DEFAULT_URL_SCHEME + u
    
    return urllib.unquote(u)

def getNewUrl(u):
    """
    mendapatkan url baru (tanpa path)
    """
    
    up = urlparse.urlparse(u)
    newurl = up.scheme + "://" + up.netloc
    return newurl

def getPage(u):
    """
    mendapatkan nama halaman (yang terakhir)
    untuk proses verifikasi
    """
    
    path = urlparse.urlparse(u).path
    
    if path in ("", "/"):
        errMsg = "page %s is not supported. " % repr(path)
        errMsg += "try using the '--admin' option to help you "
        errMsg += "find the admin login page."
        logger.error(errMsg)
        
        raise W3bruteSkipTargetException
    
    if path.endswith("/"):
        path = path.rstrip("/")
    
    page = path.split("/")
    return page[-1]

def getQuery(u):
    """
    mendapatkan daftar kueri yang ada di url
    """
    
    q = urlparse.urlparse(u).query
    
    if q == "":
        errMsg = "query not found in %s (example target 'http://www.example.com/index.php?id=4')" % repr(u)
        logger.error(errMsg)
        
        raise W3bruteNextStepException
    
    if "&" in q:
        q = q.split("&")
    else:
        q = [q]
    
    return q

def getProxy():
    """
    mendapatkan proxy dari opsi (jika digunakan)
    reference: http://www.learntosolveit.com/python/web_urllib2_proxy_auth.html 
    """
    
    proxyDict = {}
    proxy = konf.proxy
    if konf.proxyCred:
        scheme = urlparse.urlsplit(proxy).scheme + "://"
        proxy = proxy.replace(scheme, scheme + konf.proxyCred + "@")
    
    proxyDict[urlparse.urlsplit(proxy).scheme] = proxy
    return proxyDict

def getErrorMessage():
    """
    mendapatkan info `exception` yang tidak ke handle
    """
    
    excInfo = sys.exc_info()
    errMsg = "".join(traceback.format_exception(*excInfo))
    return errMsg

def getSchemeAuth(headers):
    """
    mendapatkan `scheme` atau `tipe`
    autentikasi target via HTTP header `WWW-Authenticate`
    """
    
    scheme = "basic"
    if headers.has_key("www-authenticate"):
        value = headers["www-authenticate"]
        scheme = value.split(" ", 1)[0].lower()
    
    return scheme

def pindahBaris():
    """
    memeriksa permintaan pindah ke garis baru
    dari <class 'Progress'>
    """
    
    if konf.garisBaru:
        cetakData("\n")
        del konf.garisBaru 

def getCredentialType():
    """
    mendapatkan tipe kredensial
    """
    
    credType = "account" if not auth.IS_WEBSHELL_AUTH else "password"
    return credType

def getRequestData(form):
    """
    cek jika form menggunakan aksi javascript
    """
    
    _data = list(form.click_request_data())
    _is_js = False
    
    if re.search(JAVASCRIPT_ACTION_PATTERN[1], _data[0]):
        _is_js = True
    elif re.search(JAVASCRIPT_ACTION_PATTERN[0], _data[0]):
        _is_js = True
    
    if _is_js:
        criMsg = "w3brute is not supported for "
        criMsg += "submitting forms on site interfaces "
        criMsg += "that use javascript."
        logger.critical(criMsg)
        raise W3bruteSkipTargetException
    
    _data[2] = dict(_data[2])
    req = urllib2.Request(*_data)
    
    return req

def addCredential(*values):
    """
    menambahkan kredensial
    """
    
    target.kredensial.append(values)

def checkRegexValid(response):
    """
    memeriksa jika anda menggunakan (opsi --regex-valid)
    ini digunakan untuk proses verifikasi akun/password
    """
    
    if konf.regexValid:
        if re.search(konf.regexValid, response.read()):
            status.valid = True

def resetStatus():
    """
    mengatur ulang `status` kredensial
    """
    
    status.found = status.valid = False 

def showPrompt():
    """
    memeriksa jika anda menggunakan (opsi --ask-found)
    ini digunakan untuk proses verifikasi akun/password
    """ 
    
    if konf.askFound:
        msg = "[ASK] what do you want? "
        msg += "[(C)ontinue (default) / (s)kip target / (q)uit]: "
        jawaban = raw_input(msg).lower().strip() or "c"
        if jawaban.startswith("s"):
            raise W3bruteStopBruteForceException
        elif jawaban.startswith("q"):
            konf.quit = True
            raise W3bruteStopBruteForceException
        elif jawaban.startswith("c"):
            pass
        else:
            raise W3bruteQuitException     

def checkStopSearch():
    """
    memeriksa jika anda menggunakan (opsi --stop-search)
    ini digunakan untuk mengontrol proses mencari akun.
    """ 
    
    if konf.stopSearch:
        infoMsg = "[INFO] option '--stop-search' is used. "
        infoMsg += "process of searching for an '%s' was stopped.\n" % getCredentialType()
        cetakData(infoMsg)
        raise W3bruteStopBruteForceException

def checkMaxSearch():
    """
    memeriksa jika anda menggunakan (opsi --max-search)
    ini digunakan untuk mengontrol proses mencari akun.
    """
    
    if isinstance(konf.maxSearch, int):
        if len(target.kredensial) == konf.maxSearch:
            infoMsg = "[INFO] process of searching for '%(credType)s' has reached the limit. "
            infoMsg += "try to use greater than %d (e.g. '--max-search %d') " % (konf.maxSearch, konf.maxSearch * 2) 
            infoMsg += "to search for more '%(credType)ss'.\n"
            infoMsg %= dict(credType=getCredentialType())
            cetakData(infoMsg)
            
            raise W3bruteStopBruteForceException 

def checkStatus(*cred):
    """
    memeriksa `status` kredensial
    """
    
    if (status.found or status.valid):
        stat = "potentially" if not status.valid else "valid"
        msg = "[INFO] %s -> {} (%s)" % (getCredentialType(), stat)
        pbar.newline(msg)
        info = cred + (stat,)
        addCredential(*info)
        resetStatus()
        showPrompt()
        checkStopSearch()
        checkMaxSearch()

def clearData():
    """
    membersihkan data
    """
    
    auth.clear()
    html.clear()
    target.clear() 
