from struct import Struct
from collections import OrderedDict
from itertools import izip_longest
from os import SEEK_SET

from dbpf.file import File, CompressedFile


class BaseStruct(object):
    _struct = Struct('')
    _fields = []

    def __init__(self, fileobj, *args):
        self._fileobj = fileobj
        
        self._data = OrderedDict()

        for arg, value in izip_longest(self._fields, args, fillvalue=None):
            self._data[arg] = value

    @classmethod
    def parse(cls, fileobj):
        '''takes an opened file or file-like-object and returns a 
        parsed class'''
        data = fileobj.read(cls._struct.size)
        
        return cls(fileobj, *cls._struct.unpack(data))
    
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
    

class IndexBaseStruct(BaseStruct):
    def __init__(self, *args, **kwargs):
        BaseStruct.__init__(self, *args, **kwargs)
        
        self.compressed = False
        
    def open(self):
        self._fileobj.seek(self.location, SEEK_SET)
        data = self._fileobj.read(self.size)
        
        if self.compressed:
            return CompressedFile(self._fileobj)
        else:
            return File(self._fileobj)
    
    def __repr__(self):
        fields = self._fields + ['compressed']
        
        a = ', '.join('{}={}'.format(field, getattr(self, field))
                                     for field in fields)
        return '{}({})'.format(self.__class__.__name__, a)
                              
        

class Index70(IndexBaseStruct):
    _struct = Struct('5I')
    _fields = ['type_id',
               'group_id',
               'instance_id',
               'location',
               'size']
    
class Index71(IndexBaseStruct):
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

class DIRBaseStruct(BaseStruct):
    def equals_index(self, index):
        return all(getattr(self, field) == getattr(index, field)
                   for field in self._fields[:-1])
    

class DIR70(DIRBaseStruct):
    _struct = Struct('4I')
    _fields = ['type_id',
               'group_id',
               'instance_id',
               'size']
    
class DIR71(DIRBaseStruct):
    _struct = Struct('5I')
    _fields = ['type_id',
               'group_id',
               'instance_id',
               'instance_id2',
               'size']

def dir(version):
    if isinstance(version, Header):
        version = version.index_version
    
    if version in (7.0, '7.0'):
        return DIR70
    elif version in (7.1, '7.1'):
        return DIR71
    else:
        raise NotImplementedError('Version not implemented.')