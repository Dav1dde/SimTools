from io import BytesIO
from os import SEEK_SET
from PIL import Image

from simtools import s3d
from simtools import fsh
from simtools.ext import squish

class File(object):
    _type = 'data'
    
    def __init__(self, data):
        self.data = data


class DIRFile(File):
    _type = 'DIR'


class XMLFile(File):
    _type = 'XML' 


class S3DFile(File):
    _type = 'S3D'
    
    def __init__(self, *args, **kwargs):
        File.__init__(self, *args, **kwargs)
        
        self.header = None
        self.head = None
        self.vert = None
        self.vertices = list()
        self.indx = None
        self.indices = list()
        self.prim = None
        self.primitives = list()
        self.mats = None
        self.materials = list()
        self.anim = None
        self.animations = list()
        self.prop = None
        self.properties = list()
        self.regp = None
        self.effects = list()
        
        self._parse_s3d()
    
    def _parse_s3d(self):
        io = BytesIO(self.data)
        
        self.header = s3d.Header.parse(io)
        self.head = s3d.Head.parse(io)
        
        self.vert = s3d.Vert.parse(io)
        for _ in xrange(self.vert.groups):
            group = s3d.VertexGroup.parse(io)
            
            self.vertices.append((group, [s3d.Vertex.parse(io)
                                          for _ in xrange(group.vertices)]))
        
        self.indx = s3d.Indx.parse(io)
        for _ in xrange(self.indx.groups):
            group = s3d.IndexGroup.parse(io)
            
            self.indices.append((group, [s3d.Index.parse(io)
                                         for _ in xrange(group.vertices/3)]))
        
        self.prim = s3d.Prim.parse(io)
        for _ in xrange(self.prim.groups):
            self.primitives.append(s3d.PrimGroup.parse(io))
        
        
        self.mats = s3d.Mats.parse(io)
        Group = s3d.MaterialGTE15 if float(self.head.version) >= 1.5 \
                    else s3d.MaterialLT15
        for _ in xrange(self.mats.groups):
            self.materials.append(Group.parse(io))
        
        
        self.anim = s3d.Anim.parse(io)
        for _ in xrange(self.anim.groups):
            self.animations.append(s3d.AnimationGroup.parse(io))
        
        self.prop = s3d.Prop.parse(io)
        for _ in xrange(self.prop.groups):
            self.properties.append(s3d.PropertyGroup.parse(io))
        
        self.regp = s3d.Regp.parse(io)
        for _ in xrange(self.regp.effects):
            group = s3d.EffectGroup.parse(io)
            
            self.effects.append((group, [s3d.Effect.parse(io)
                                         for _ in xrange(group.effects)]))
            
        


class ImageFile(File):
    _type = ('BMP', 'JPEG')
    
    def pil_image(self):
        return Image.open(BytesIO(self.data))
         

class FSHFile(ImageFile):
    _type = 'FSH'
    
    def __init__(self, *args, **kwargs):
        File.__init__(self, *args, **kwargs)
        
        self.header = None
        self.directory = None
        self.entry_header = None
        
        self._parse_fsh()
    
    def _parse_fsh(self):
        io = BytesIO(self.data)
        
        self.header = fsh.Header.parse(io)
        self.directory = fsh.Directory.parse(io)
        io.seek(self.directory.offset, SEEK_SET)
        
        self.entry_header = fsh.EntryHeader.parse(io)
        
        #assert(self.entry_header.size == 0)
        compression = None
        if self.entry_header.record_id == 0x60:
            compression = squish.DXT1
        elif self.entry_header.record_id == 0x61:
            compression = squish.DXT3
        
        if not compression is None:
            self.data = squish.decompress_image(self.data, self.entry_header.width,
                                                           self.entry_header.height,
                                                compression)
    
    @property
    def size(self):
        return (self.entry_header.width, self.entry_header.height)
    
    def pil_image(self):
        return Image.fromstring('RGBA', self.size, self.data)

