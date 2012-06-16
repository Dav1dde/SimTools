from struct import Struct, unpack, pack

from simtools.util import BaseStruct


class Header(BaseStruct):
    _struct = Struct('<4sI')
    _fields = ['magic',
               'size']


class Head(BaseStruct):
    _struct = Struct('<4sI2H')
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
    _struct = Struct('<4s2I')
    _fields = ['magic',
               'size',
               'groups']

class VertexGroup(BaseStruct):
    _struct = Struct('<2HI')
    _fields = ['flags',
               'vertices',
               'format']

class Vertex(BaseStruct):
    _struct = Struct('<5f')
    _fields = ['x',
               'y',
               'z',
               'u',
               'v']


class Indx(BaseStruct):
    _struct = Struct('<4s2I')
    _fields = ['magic',
               'size',
               'groups']
    
class IndexGroup(BaseStruct):
    _struct = Struct('<3H')
    _fields = ['flags',
               'stride',
               'vertices'] # / 3 to get the triangles]
    
class Index(BaseStruct):
    _struct = Struct('<3H')
    _fields = ['a',
               'b',
               'c']
    
    
class Prim(BaseStruct):
    _struct = Struct('<4s2I')
    _fields = ['magic',
               'size',
               'groups']
    
class PrimGroup(BaseStruct):
    _struct = Struct('<H3I')
    _fields = ['primitives',
               'type',
               'vertex',
               'vertices_per_group']


class Mats(BaseStruct):
    _struct = Struct('<4s2I')
    _fields = ['magic',
               'size',
               'groups']

class Material(BaseStruct):
    @classmethod
    def parse(cls, fileobj):
        data = cls._struct.unpack(fileobj.read(cls._struct.size))
        
        name_length, = unpack('B', fileobj.read(1))
        name = unpack(str(name_length) + 's', fileobj.read(name_length))[0].lstrip('\x00')
        
        return cls(fileobj, *(data + (name,)))
    

class MaterialGTE15(Material):
    _struct = Struct('<I4BHI2BI4B2H')
    _fields = ['flags',
               'alpha_func',
               'depth_func',
               'source_blend',
               'destination_blend',
               'alpha_threshold',
               'material_class',
               'reserved',
               'texture_count',
               'instance_id',
               'wrap_mode_u',
               'wrap_mode_v',
               'magnification_filter',
               'minification_filter',
               'animation_rate',
               'animation_mode',
               'name']
    
    def raw(self):
        return self._struct.pack(*self._data.values()[:16]) + \
            pack('<B{}s'.format(len(self.name)), len(self.name), self.name+'\x00')
    

class MaterialLT15(Material):
    _struct = Struct('<I4BHI2BI2B2H')
    _fields = ['flags',
               'alpha_func',
               'depth_func',
               'source_blend',
               'destination_blend',
               'alpha_threshold',
               'material_class',
               'reserved',
               'texture_count',
               'instance_id',
               'wrap_mode_u',
               'wrap_mode_v',
               'animation_rate',
               'animation_mode',
               'name']
    
    def raw(self):
        return self._struct.pack(*self._data.values()[:14]) + \
            pack('<B{}s'.format(len(self.name)+1), len(self.name)+1, self.name + '\x00')


class Anim(BaseStruct):
    _struct = Struct('<4sI3HIfH')
    _fields = ['magic',
               'size',
               'frames_per_assignment_groups',
               'frame_rate',
               'mode',
               'flags',
               'displacement',
               'groups']

class AnimationGroup(BaseStruct):
    _fields = ['name',
               'flags',
               'vertex_block_index',
               'index_block_index',
               'primitive_block_index',
               'material_block_index']

    @classmethod
    def parse(cls, fileobj):
        length, = unpack('B', fileobj.read(1))
        flags, = unpack('B', fileobj.read(1))
        name = unpack(str(length) + 's', fileobj.read(length))[0].lstrip('\x00')
        indices = unpack('<4H', fileobj.read(8))
        
        return cls(fileobj, name, flags, *indices)

    def raw(self):
        return pack('<BB{}s4H'.format(len(self.name)),
                    len(self.name), self.flags, self.name,
                    self.vertex_block_index, self.index_block_index,
                    self.primitive_block_index, self.material_block_index)


class Prop(BaseStruct):
    _struct = Struct('<4s2I')
    _fields = ['magic',
               'size',
               'groups']

class PropertyGroup(BaseStruct):
    _fields = ['mesh_index',
               'frame_number',
               'type',
               'property_name']
       
    @classmethod
    def parse(cls, fileobj):
        mesh_index, frame_number = unpack('2H', fileobj.read(4))
        type_length = unpack('B', fileobj.read(1))
        type = unpack(str(type_length) + 's', fileobj.read(type_length)).lstrip('\x00')
        
        property_name_length = unpack('B', fileobj.read(1))
        property_name = unpack(str(property_name_length) + 's', fileobj.read(property_name_length)).lstrip('\x00')
        
        return cls(fileobj, mesh_index, frame_number, type, property_name)

    def raw(self):
        return pack('<2HB{}sB{}s'.format(len(self.type),
                                         len(self.property)),
                    self.mesh_index, self.frame_number,
                    len(self.type), self.type,
                    len(self.property_name), self.property_name)


class Regp(BaseStruct):
    _struct = Struct('<4s2I')
    _fields = ['magic',
               'size',
               'effects']

class EffectGroup(BaseStruct):
    _fields = ['name',
               'effects']

class Effect(BaseStruct):
    _struct = Struct('<3f4f') # TODO: verify
    _fields = ['translation_x',
               'translation_y',
               'translation_z',
               'orientation_x',
               'orientation_y',
               'orientation_z',
               'orientation_w'] 
        
        