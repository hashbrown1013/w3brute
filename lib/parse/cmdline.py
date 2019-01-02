#!/usr/bin/env python

# Copyright (c) 2018 W3brute Developers.
# See LICENSE for more details.

import optparse
import os
import sys

from lib.core.common import is_db
from lib.core.common import getTerminalSize
from lib.core.data import defaults
from lib.core.settings import HOMEPAGE
from lib.core.settings import VERSION_STRING
from lib.core.settings import FILE_FORMAT
from lib.core.settings import URL_SCHEMES
from lib.core.settings import IS_WIN
from lib.utils.option import PrettyHelpFormatter

def cmdLineParser():
    """
    konfigurasi optparse
    """
    
    prog = os.path.basename(sys.argv[0])
    usage = "%s" % (prog if IS_WIN else "python " + prog)
    usage += " [options]"
    
    parser = optparse.OptionParser(usage=usage, formatter=PrettyHelpFormatter())
    parser.disable_interspersed_args()
    
    try:
        parser.add_option("-v", "--version", dest="version", action="store_true", help="show program's version number and exit")
        
        # Target options.
        target = optparse.OptionGroup(parser, "Target", "this option is used to get or enter a specific target(s).")
        
        target.add_option("-t", "--target", dest="targetUrl", metavar="url", help="target URL (e.g. http://www.example.com/admin/login.php)")
        target.add_option("-l", dest="targetFile", metavar="file", help="load target from file (e.g. /path/to/target.txt)")
        target.add_option("-g", dest="googleDork", metavar="dork", help="find target(s) with google dork (e.g. inurl:/adm/medsos.php)")
        
        # Credential options.
        credential = optparse.OptionGroup(parser, "Credential", "this option is used to enter a list of usernames, passwords and domains. "
            "which will be used to find target account / password.")
        
        credential.add_option("-u", "--user", dest="usernames", metavar="username", help="username or FILE (e.g. /path/to/usernames.txt)")
        credential.add_option("-p", "--pass", dest="passwords", metavar="password", help="password or FILE (e.g. /path/to/passwords.txt)")
        credential.add_option("-d", "--domain", dest="domain", help="email domain (default %s)" % defaults.domain)
        
        # Request options.
        request = optparse.OptionGroup(parser, "Request", "this option is used to connect to target.")
        
        request.add_option("--agent", dest="agent", help="HTTP User-Agent header value to send to server")
        request.add_option("--timeout", dest="timeout", metavar="seconds", type="float", help="socket timeout (default %d)" % defaults.timeout)
        request.add_option("--retries", dest="retries", type="int", help="limit repeats connection if connection has a problem (default %d)" % defaults.retries)
        request.add_option("--delay", dest="delay", metavar="seconds", type="float", help="waiting time when response connection is problematic (default %d)" % defaults.delay)
        request.add_option("--proxy", dest="proxy", help="use a proxy to connect to target (e.g. http://127.0.0.1:8080)")
        request.add_option("--proxy-cred", dest="proxyCred", metavar="cred", help="proxy credentials (e.g. username:password)", default="DONT_MAKE_UNIQUE_OPTION")
        
        # Scanner options.
        scanner = optparse.OptionGroup(parser, "Scanner", "this option is used to help you find / get target information")
        
        scanner.add_option("--sqli", dest="sqliScanner", action="store_true", help="SQL injection scanner vulnerability")
        scanner.add_option("--admin", dest="adminScanner", action="store_true", help="admin page scanner")
        
        # Attack options.
        attack = optparse.OptionGroup(parser, "Attack", "this option is used to select attack method to be used.")
        
        attack.add_option("--sqli-bypass", dest="sqliBypass", action="store_true", help="SQL injection bypass authentication technique")
        attack.add_option("--mixed-cred", dest="mixedCred", action="store_true", help="mixed credentials (username + SQL injection query)")
        
        # Controller options.
        controller = optparse.OptionGroup(parser, "Controller", "this option is used to control account lists and brute force attack sessions.")
        
        controller.add_option("--slice-user", dest="sliceUser", metavar="slice", help="slicing username from list")
        controller.add_option("--slice-pass", dest="slicePass", metavar="slice", help="slicing password from list") 
        controller.add_option("--stop-search", dest="stopSearch", action="store_true", help="stop brute force process if you have found a potential account")
        controller.add_option("--max-search", dest="maxSearch", metavar="int", type="int", help="limit for searching for potential accounts")
        
        # Verifying options.
        verifying = optparse.OptionGroup(parser, "Verifying", "this option is used for verification process if account or password (web shell) is valid")
        verifying.add_option("--ask-found", dest="askFound", action="store_true", help="prompt to ask for an answer if you find a potential account")
        verifying.add_option("--regex-valid", dest="regexValid", metavar="regex", type="string", help="regex to find out if account is valid (e.g. '(?i)Dashboard')")
        
        # Other options.
        other = optparse.OptionGroup(parser, "Other")
        other.add_option("--output-dir", dest="outputDir", metavar="dir", help="output directory (default %s)" % defaults.outputDir)
        other.add_option("--rest-name", dest="filename", help="result file name (default %s)" % repr(defaults.filename))
        other.add_option("--rest-format", dest="fileFormat", metavar="format", choices=FILE_FORMAT[1:], help="result file format (%s (default), HTML, or SQLITE3)" % defaults.fileFormat.upper())
        other.add_option("--admin-paths", dest="adminPaths", metavar="file", help="list admin page to scan")
        other.add_option("--google-page", dest="googlePage", metavar="page", type="int", help="google page that will be scanned (default %d)" % defaults.googlePage)
        
        # fitur ini, hanya untuk lebar terminal kurang dari atau sama dengan 50
        # seperti layar smartphone?.
        if getTerminalSize()[0] <= 50:
            other.add_option("--disable-wrap", dest="disableWrap", action="store_true", help="disable line wrapping")
        
        other.add_option("--no-color", dest="noColor", action="store_true", help="disable color for output text in terminal")
        
        parser.add_option_group(target)
        parser.add_option_group(credential)
        parser.add_option_group(request)
        parser.add_option_group(scanner)
        parser.add_option_group(attack)
        parser.add_option_group(controller)
        parser.add_option_group(verifying)
        parser.add_option_group(other)
        
        def smartCapitalize(object_):
            """
            fungsi untuk mengubah karakter (huruf awal) string
            ke huruf besar (kapital), jika huruf awal adalah huruf kecil. 
            """
            
            awal = object_[0]
            if awal.isalpha() and awal.islower():
                # ubah huruf awal saja menjadi huruf kapital.
                object_ = awal.upper() + object_[1:]
            
            return object_
        
        opt = parser.get_option("-h")
        opt.help = smartCapitalize(opt.help)
        opt = parser.get_option("-v")
        opt.help = smartCapitalize(opt.help)
        
        def makeUniqueShortOption(long_opt):
            """ membuat opsi pendek unik
            
            long_opt = --hello-world
            
            :return: -hW
            
            """
            
            opt = long_opt.lstrip("-").split("-")
            uniqueOpt = "-" + opt[0][0] + opt[1][0].upper()
            return uniqueOpt
                
        # persiapan untuk membuat opsi unik
        uniqueOptDict = dict()
        for groups in parser.option_groups:
            options = groups.option_list
            for option in options:
                if len(option._short_opts) == 0 and len(option._long_opts) == 1:
                    long_opt = option.get_opt_string()
                    if long_opt.count("-") == 3:
                        if option.default != "DONT_MAKE_UNIQUE_OPTION":
                            uniqueOpt = makeUniqueShortOption(long_opt)
                            if uniqueOpt not in uniqueOptDict.keys():
                                # mengatur opsi unik ke optparse
                                option._short_opts = [uniqueOpt]
                                # simpan opsi unik
                                uniqueOptDict[uniqueOpt] = long_opt
                        else:
                            # kembalikan nilai default opsi ke None
                            parser.set_default(option.dest, None)
                
                option.help = smartCapitalize(option.help)
        
        def isUniqueOption(opt):
            """
            memeriksa jika objek adalah
            opsi unik.
            """
            
            if opt.startswith("-") and opt.count("-") == 1:
                name = opt.lstrip("-")
                if len(name) >= 2:
                    return True
            return False
        
        def prepareOption(argv):
            """
            memeriksa opsi unik
            dan mengembalikan opsi unik ke opsi normal
            """
            
            for i in xrange(len(argv)):
                option = argv[i]
                if option not in uniqueOptDict.keys():
                    if isUniqueOption(option):
                        raise optparse.BadOptionError(option)
                else:
                    # kembalikan opsi unik ke opsi normal
                    argv[i] = uniqueOptDict[option]
            
            return argv
        
        args = prepareOption(sys.argv)[1:]
        (options, _) = parser.parse_args(args)
        
        if options.version:
            msg = "(%s) %s\n" % (VERSION_STRING, HOMEPAGE)
            cetakData(msg)
            
            raise SystemExit 
        
        if not any([options.targetUrl, options.targetFile, options.googleDork]):
            msg = "you must use option ('-t', '-l' or '-g') "
            msg += "to run w3brute. try '-h' for more information"
            parser.error(msg)
            
            raise SystemExit 
        
        if options.targetUrl \
            and os.path.isfile(options.targetUrl):
                msg = "invalid type: %s (use the '-l' option to load target from file)" % options.targetUrl
                parser.error(msg)
                
                raise SystemExit
        
        opsiVal = (options.targetFile, options.usernames, options.passwords, options.domain, options.adminPaths)
        for _ in opsiVal:
            if _ and is_db(_):
                errMsg = "invalid type: " + _
                parser.error(errMsg)
                
                raise SystemExit
        
        if options.proxy:
            if not options.proxy.startswith(URL_SCHEMES):
                parser.error("invalid proxy %s (e.g. http://127.0.0.1:8080/)" % options.proxy)
                
                raise SystemExit
            
            if options.proxyCred \
                and options.proxyCred.count(":") != 1:
                    parser.error("invalid proxy credential %s (e.g. username:password)" % repr(options.proxyCred))
                    
                    raise SystemExit
        
        if options.stopSearch \
            and options.maxSearch:
                msg = "clash option! you have to choose one option ('--stop-search' or '--max-search')"
                parser.error(msg)
                
                raise SystemExit
        
        if options.maxSearch \
            and options.maxSearch <= 1:
                msg = "option value '--max-search' must be greater than 1"
                parser.error(msg)
                
                raise SystemExit
        
        return options
    
    except (optparse.OptionError, optparse.BadOptionError, TypeError), ex:
        parser.error(ex)
