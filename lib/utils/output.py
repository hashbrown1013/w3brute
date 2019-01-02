#!/usr/bin/env python

# Copyright (c) 2018 W3brute Developers.
# See LICENSE for more details.

import csv
import sqlite3

from lib.core.common import randomHexColor
from lib.core.settings import HTML_FORMAT
from lib.core.settings import FILE_FORMAT

class OutputWriter(object):
    """
    simpel mesin pembuat file hasil
    didukung tipe file format (csv, html or sqlite3)
    format csv (default)
    """
    
    def __init__(self, fp, fieldnames, format):
        self.fp = fp
        self.fieldnames = fieldnames
        
        if format.lower() not in FILE_FORMAT:
            raise TypeError("file format: %s is not supported" % repr(format))
        
        if format.lower() == "sqlite3":
            self.fp = sqlite3.connect(fp.name)
        
        self.format = format
        self._html_table = "<table id=\"result_w3brute\">\n"
        
        self.init()
    
    def init(self):
        if self.format == "csv":
            self.writer = csv.DictWriter(self.fp, self.fieldnames)
            self.writer.writeheader()
        
        elif self.format == "sqlite3":
            # buat table untuk tempat hasil.
            # table:
            # 1.) accounts; untuk daftar akun
            # 2.) passwords; untuk daftar password (web shell)
            
            self.table_name = "accounts" if len(self.fieldnames) > 3 else "passwords"
            self.fieldnames.pop(0)
            self.fieldnames.insert(0, "id")
            # tipe parameter table
            types = ["INTEGER"] + (["TEXT"] * len(self.fieldnames[1:]))
            # parameter table
            param = ""
            for _ in zip(self.fieldnames, types):
                param += " ".join(_) + ", "
            
            param = param[:-2]
            data = dict(name=self.table_name, param=param)
            self.cursor = self.fp.cursor()
            self.cursor.execute("create table %(name)s (%(param)s)" % data)
        
        else:
            self._html_table += "            <tr>\n"
            for header in self.fieldnames:
                self._html_table += "                <th>%s</th>\n" % header
            
            self._html_table += "            </tr>\n"
    
    def add_row(self, *args):
        if self.format == "csv":
            row = dict()
            for i in range(len(args)):
                key = self.fieldnames[i]
                value = args[i]
                row[key] = value
            
            self.writer.writerow(row)
        
        elif self.format == "sqlite3":
            param = ", ".join(list("?" * len(args)))
            data = dict(table=self.table_name, param=param)
            self.cursor.execute("insert into %(table)s values(%(param)s)" % data, args)
        
        else:
            self._html_table += "            <tr>\n"
            
            for _ in args:
                self._html_table += "                <td>%s</td>\n" % _
            
            self._html_table += "            </tr>\n"
    
    def close(self):
        """
        tutup file dan simpan
        """
        
        if self.format == "csv":
            self.fp.close()
        
        elif self.format == "sqlite3":
            self.fp.commit()
            self.fp.close()
        
        else:
            self._html_table += "        </table>"
            html = HTML_FORMAT.substitute(html_table=self._html_table, bg_color=randomHexColor())
            self.fp.write(html)
            self.fp.close()
