#!/usr/bin/env python

# Copyright (c) 2018 W3brute Developers.
# See LICENSE for more details.

class PyDict(dict):
    """
    >>> beli = PyDict()
    >>> beli.cewe = 1
    >>> beli.cewe
    1
    
    >>> beli = PyDict(perawan=1, janda=2)
    >>> beli.perawan
    1
    >>> beli.janda
    2
    
    """
    
    def __init__(self, data={}, **kwargs):
        # initialisasi data
        kwargs.update(data)
        
        dict.__init__(self, kwargs)
    
    def __setattr__(self, name, value):
        # atur atribut --> x.item = value
        self.__setitem__(name, value)
    
    def __getattr__(self, name):
        # mendapatkan nilai atribut --> x.item
        return self.__getitem__(name)
    
    def __delattr__(self, name):
        # menghapus atribut --> del x.item
        self.__delitem__(name)
    
    def __getitem__(self, name):
        # mendapatkan nilai item -> x["item"]
        try:
            return dict.__getitem__(self, name)
        except KeyError:
            return None # jika item tidak ada di dict
    
    # def __getstate__(self):
    #     return self.__dict__
    #
    # def __setstate__(self, dict):
    #     self.__dict__ = dict
    #
    # def copy(self):
    #     import cPickle
    #     return cPickle.loads(cPickle.dumps(self))
