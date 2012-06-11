from struct import Struct

from simtools.util import BaseStruct


class Header(BaseStruct):
    _struct = Struct('4sI')
    _fields = ['magic',
               'size']


class Head(BaseStruct):
    _struct = Struct('4sI2H')
    _fields = ['magic',
               'size',
               'version_major',
               'version_minor']

    @property
    def version(self):
        return u'.'.join([unicode(self.version_major), unicode(self.version_minor)])
    
    @version.setter
    def version(self, version):
        self.version_major, self.version_minor = map(int, version.split('.'))


class Vert(BaseStruct):
    _struct = Struct('4s2I2HI')
    _fields = ['magic',
               'size',
               'vertex_groups',
               'flags',
               'vertices_per_group',
               'format']

