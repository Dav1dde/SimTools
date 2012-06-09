from struct import Struct
from collections import OrderedDict
from itertools import izip_longest


class BaseStruct(object):
    _struct = Struct('')
    _fields = []

    def __init__(self, *args):
        self._data = OrderedDict()
    
        for arg, value in izip_longest(self._fields, args, None):
            self._data[arg] = value

    @staticmethod
    def parse(cls, fileobj):
        '''takes an opened file or file-like-object and returns a 
        parsed Header class'''
        header = fileobj.read(cls._struct.size)
        
        return cls(cls._struct.unpack(header))
    
    @property
    def raw(self):
        return self._struct.pack(*self._data.values())
    
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



class Header(BaseStruct):
    _struct = Struct('<4s17i24s')
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

    @property
    def version(self):
        return u'.'.join([unicode(self.version_major), unicode(self.version_minor)])
    
    @property
    def user_version(self):
        return u'.'.join([unicode(self.user_version_major), unicode(self.user_version_minor)])
    

class Index70(BaseStruct):
    _struct = Struct('<5i')
    _fields = ['type_id',
               'group_id',
               'instance_id',
               'location',
               'size']
    
class Index71(BaseStruct):
    _struct = Struct('<6i')
    _fields = ['type_id',
               'group_id',
               'instance_id',
               'instance2_id',
               'location',
               'size']
    
def index(version):
    if version in (7.0, '7.0'):
        return Index70
    elif version in (7.1, '7.1'):
        return Index71
    else:
        raise NotImplementedError('Version not implemented.')


class Hole(BaseStruct):
    _struct = Struct('<2i')
    _fields = ['location',
               'size']
    