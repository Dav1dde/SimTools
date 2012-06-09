from struct import Struct
from collections import OrderedDict
from itertools import izip_longest

HEADER_STRUCT = Struct('<4s17i24s')
HEADER_SIZE = HEADER_STRUCT.size

class Header(object):
    _fields = ('magic',
               'version_major', 'version_minor',
               'user_version_major', 'user_version_minor',
               'flags',
               'ctime', 'mtime',
               'index_version_major',
               'index_count', 'index_offset', 'index_size',
               'holes_count', 'holes_offset', 'holes_size',
               'index_version_minor',
               'index_offfset2',
               'unknown',
               'reserved')

    def __init__(self, *args):
        self._data = OrderedDict()
    
        for arg, value in izip_longest(self._fields, args, None):
            self._data[arg] = value
    
    @property
    def version(self):
        return u'.'.join([unicode(self.version_major), unicode(self.version_minor)])
    
    @property
    def user_version(self):
        return u'.'.join([unicode(self.user_version_major), unicode(self.user_version_minor)])
    
    @property
    def raw(self):
        return HEADER_STRUCT.pack(*self._data.values())
    
    def __getattr__(self, name):
        if name in self._fields:
            return self._data[name]
        else:
            super(Header, self).__getattr__(name)
    
    def __setattr__(self, name, value):
        if name in self._fields:
            self._data[name] = value
        else:
            super(Header, self).__setattr__(name)
    
    @staticmethod
    def parse(cls, fileobj):
        '''takes an opened file or file-like-object and returns a 
        parsed Header class'''
        header = fileobj.read(HEADER_SIZE)
        
        return cls._make(HEADER_STRUCT.unpack(header))