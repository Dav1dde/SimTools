from struct import Struct

from simtools.util import BaseStruct


class Header(BaseStruct):
    _struct = Struct('4s2I4s')
    _fields = ['magic',
               'file_size',
               'entry_count',
               'directory_id']


class Directory(BaseStruct):
    _struct = Struct('4sI')
    _fields = ['entry_name',
               'offset']
    

class EntryHeader(BaseStruct):
    _struct = Struct('b3b6H')
    _fields = ['record_id',
               'size1',
               'size2',
               'size3',
               'width',
               'height',
               'x_center',
               'y_center',
               'x_left',
               'y_top']
    
    @property
    def size(self):
        return self.size1 << 16 | self.size2 << 8 | self.size3
    
    @size.setter
    def size(self, value):
        self.size1 = value >> 16
        self.size2 = (value >> 8) & 0xff
        self.size3 = value & 0xff