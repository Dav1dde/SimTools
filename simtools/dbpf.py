from struct import Struct
from os import SEEK_SET

from simtools.qfs import decompress
from simtools.util import BaseStruct
from simtools.magic import magic_index


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
            header, data = decompress(data)
        
        type = magic_index(self)

        return type.cls(data)
    
    def __repr__(self):
        fields = self._fields + ['compressed']
        
        a = ', '.join('{}={}'.format(field, getattr(self, field))
                                     for field in fields)
        return '{}({})'.format(self.__class__.__name__, a)
                              
        

class Index70(IndexBaseStruct):
    _struct = Struct('<5I')
    _fields = ['type_id',
               'group_id',
               'instance_id',
               'location',
               'size']
    
class Index71(IndexBaseStruct):
    _struct = Struct('<6I')
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
    _struct = Struct('<2I')
    _fields = ['location',
               'size']

class DIRBaseStruct(BaseStruct):
    def equals_index(self, index):
        return all(getattr(self, field) == getattr(index, field)
                   for field in self._fields[:-1])
    

class DIR70(DIRBaseStruct):
    _struct = Struct('<4I')
    _fields = ['type_id',
               'group_id',
               'instance_id',
               'size']
    
class DIR71(DIRBaseStruct):
    _struct = Struct('<5I')
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