from struct import Struct
from collections import OrderedDict
from itertools import izip_longest
from io import BufferedIOBase


class BaseStruct(object):
    _struct = Struct('')
    _fields = []

    def __init__(self, *args):
        if args and isinstance(args[0], (file, BufferedIOBase)):
            self._fileobj = args[0]
            args = args[1:]
        else:
            self._fileobj = None
        
        self._data = OrderedDict()

        for arg, value in izip_longest(self._fields, args, fillvalue=None):
            self._data[arg] = value

    @classmethod
    def parse(cls, fileobj):
        '''takes an opened file or file-like-object and returns a 
        parsed class'''
        data = fileobj.read(cls._struct.size)
        
        return cls(fileobj, *cls._struct.unpack(data))
    
    def raw(self):
        return self._struct.pack(*self._data.values())
    
    def __getattr__(self, name):
        if name in self._fields:
            return self._data[name]
        else:
            raise AttributeError, name
        
    def __setattr__(self, name, value):
        if name in self._fields:
            self._data[name] = value
        else:
            object.__setattr__(self, name, value)

    def __cmp__(self, other):
        if isinstance(other, BaseStruct):
            return self._data == other._data
        else:
            return False

    def __hash__(self):
        return hash(self._data)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__,
                               ', '.join('{}={}'.format(field, 
                                                        getattr(self, field))
                                         for field in self._fields))
    
    
def enforce(boolean, exception, *args, **kwargs):
    if not boolean:
        raise exception(*args, **kwargs)