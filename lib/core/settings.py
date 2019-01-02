#!/usr/bin/env python

# Copyright (c) 2018 W3brute Developers.
# See LICENSE for more details.

import string
import subprocess

AUTHOR = "Aprila Hijriyan"
VERSION = "1.0"
VERSION_STRING = "w3brute-%s#dev" % VERSION
DESCRIPTION = "Automatic Web Application Brute Force Attack Tool"
HOMEPAGE = "https://github.com/aprilahijriyan/w3brute"
LICENSE = "LGPLv3"

BANNER = r"""
                        /',            ,'\
                       /gg\            /gg\
                      /g.gg\          /gg.g\
                     |gg..gg\        /gg..gg|
                     |gg...g|        |g...gg|
                     |gg...g|        |g...gg|
                      \gg..g/        \g..gg/
                       )gg.gvgggggggggvg.gg(
                      /ggggggggggggggggggggg\
                     /gggg(((ggggggggg)))gggg\
                     |ggggg....ggggg....ggggg|
                     |ggggg....ggggg....ggggg|
                     |ggcccgggg\___/ggggcccgg|
                     |ggcccccgggg|ggggcccccgg|
                       \gcccggg\---/gggcccg/
                          \ggggggggggggg/
                        
                         (%(VERSION)s)
              %(HOMEPAGE)s
        _______________________________________________________
+ -- -=[ Automatic Web Application Brute Force Attack Tool     ]
+ -- -=[ Supported Web Types: Web Shell, HTTP 401 UNAUTHORIZED ]
+ -- -=[_______________________________________________________]

"""

# reference: https://www.w3schools.com/css/css_table.asp 
HTML_FORMAT = string.Template("""\
<html>
    <title>W3brute - Automatic Web Application Brute Force Attack Tool</title>
    <head>
        <style type=\"text/css\">
            #result_w3brute {
                font-family: \"Trebuchet MS\", Arial, Helvetica, sans-serif;
                border-collapse: collapse;
                width: 100%;
            }
            
            #result_w3brute td, #result_w3brute th {
                border: 1px solid #ddd;
                padding: 8px;
            }
            
            #result_w3brute tr:nth-child(even) {
                background-color: #f2f2f2;
            }
            
            #result_w3brute tr:hover {
                background-color: #ddd;
            }
            
            #result_w3brute th {
                padding-top: 12px;
                padding-bottom: 12px;
                text-align: left;
                background-color: ${bg_color};
                color: white;
            }
        </style>
    </head>
    <body>
        ${html_table}
    </body>
</html>\
""")

FILE_FORMAT = ("csv", "html", "sqlite3")

URL_SCHEMES = ("http://", "https://")

DEFAULT_URL_SCHEME = URL_SCHEMES[0]

SPINNER_CHAR = list("|/-\\")

EMAIL_PATTERN = "[\w\.-]+@[\w\.-]+"

ZIP_PATTERN = ".*;[\w.-]+(?:$|\:.*$)"

DB_PATTERN = ".*>[\w.]+;.*"

ADMIN_PAGE_RESPONSE = (200, 401)

SQL_PAYLOAD = ("'", "\\")

SQL_ERROR_MESSAGE = ("You have an error in your.+", "Warning:.+\(\)")

JAVASCRIPT_ACTION_PATTERN = ("(?i)javascript:", "(?i)javascript?\:(?:[;]*|.+?\(\))|.+?\(\)")

IS_WIN = subprocess.mswindows