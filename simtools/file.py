from io import BytesIO
from os import SEEK_SET
from PIL import Image

from simtools import fsh
from simtools.ext import squish

class File(object):
    _type = 'data'
    
    def __init__(self, data):
        self.data = data


class XMLFile(File):
    _type = 'XML' 


class S3DFile(File):
    _type = 'S3D'


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


