from struct import Struct
from collections import OrderedDict
from itertools import izip_longest, chain


class BaseStruct(object):
    _struct = Struct('')
    _fields = []

    def __init__(self, *args):
        self._data = OrderedDict()

        for arg, value in izip_longest(self._fields, args, fillvalue=None):
            self._data[arg] = value

    @classmethod
    def parse(cls, fileobj):
        '''takes an opened file or file-like-object and returns a 
        parsed class'''
        data = fileobj.read(cls._struct.size)
        
        return cls(*cls._struct.unpack(data))
    
    @property
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

    def __repr__(self):
        return repr(self._data).replace('OrderedDict', self.__class__.__name__)


class Header(BaseStruct):
    _struct = Struct('4s17i24s')
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
    
    @version.setter
    def version(self, version):
        self.version_major, self.version_minor = map(int, version.split('.')) 
        
    @property
    def user_version(self):
        return u'.'.join([unicode(self.user_version_major), unicode(self.user_version_minor)])
    
    @user_version.setter
    def user_version(self, version):
        self.user_version_major, self.user_version_minor = map(int, version.split('.')) 
        
    @property
    def index_version(self):
        return u'.'.join([unicode(self.index_version_major), unicode(self.index_version_minor)])
    
    @index_version.setter
    def index_version(self, version):
        self.index_version_major, self.index_version_minor = map(int, version.split('.')) 
    

class Index70(BaseStruct):
    _struct = Struct('5I')
    _fields = ['type_id',
               'group_id',
               'instance_id',
               'location',
               'size']
    
class Index71(BaseStruct):
    _struct = Struct('6I')
    _fields = ['type_id',
               'group_id',
               'instance_id',
               'instance2_id',
               'location',
               'size']

def index(version):
    if isinstance(version, Header):
        version = version.index_version
    
    if version in (7.0, '7.0'):
        return Index70
    elif version in (7.1, '7.1'):
        return Index71
    else:
        raise NotImplementedError('Version not implemented.')
    
class Hole(BaseStruct):
    _struct = Struct('2I')
    _fields = ['location',
               'size']

class DIR70(BaseStruct):
    _struct = Struct('4I')
    _fields = ['type_id',
               'group_id',
               'instance_id',
               'location',
               'size']
    
    @classmethod
    def parse(cls, fileobj, location):
        data = list(cls._struct.unpack(fileobj.read(cls._struct.size)))
        data.insert(-1, location)        
        
        return cls(*data)
        

class DIR71(BaseStruct):
    _struct = Struct('5I')
    _fields = ['type_id',
               'group_id',
               'instance_id',
               'instance_id2',
               'location',
               'size']
    
    @classmethod
    def parse(cls, fileobj, location):
        data = list(cls._struct.unpack(fileobj.read(cls._struct.size)))
        data.insert(-1, location)        
        
        return cls(*data)

def dir(version):
    if isinstance(version, Header):
        version = version.index_version
    
    if version in (7.0, '7.0'):
        return DIR70
    elif version in (7.1, '7.1'):
        return DIR71
    else:
        raise NotImplementedError('Version not implemented.')