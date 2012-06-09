from dbpf.header import Header, Hole, index, dir
from os import SEEK_SET


class DBPF(object):
    def __init__(self, file=None, ignore_magic=False):
        self.ignore_magic = ignore_magic
        
        self.header = None
        self.indices = []
        self.holes = []
        self.DIR = []
        
        if not file is None:
            self.parse_file(file)
    
    def parse_file(self, file_or_path):
        if isinstance(file_or_path, basestring):
            with open(file_or_path) as f:
                self._parse_file(f)
        else:
            self._parse_file(file_or_path)
    
    def _parse_file(self, fileobj):
        self.header = Header.parse(fileobj)
        
        if not self.ignore_magic:
            if not self.header.magic == 'DBPF':
                raise ValueError('This is not a valid DBPF file.')
        
        if not self.header.version == '1.0':
            raise ValueError('DBPF Version not supported')
        
        self._extract_indices(fileobj)
        self._extract_holes(fileobj)
        self._get_dir(fileobj)
    
    def _extract_indices(self, fileobj):
        if self.header.index_count >= 1:
            Index = index(self.header.index_version)
            
            fileobj.seek(self.header.index_offset, SEEK_SET)
            
            for _ in xrange(self.header.index_count):
                self.indices.append(Index.parse(fileobj))
            
            if not fileobj.tell() == (self.header.index_offset + self.header.index_size):
                raise ValueError('incorrect amount of data read, file to small?')
    
    def _extract_holes(self, fileobj):
        if self.header.holes_count >= 1:
            fileobj.seek(self.header.holes_offset, SEEK_SET)
            
            for _ in xrange(self.header.holes_count):
                self.holes.append(Hole.parse(fileobj))
                
            if not fileobj.tell() == (self.header.holes_offset + self.header.holes_size):
                raise ValueError('incorrect amount of data read, file to small?')
            
    def _get_dir(self, fileobj):
        for index in self.indices:
            if index.type_id == 0xe86b1eef:
                DIR = dir(self.header.index_version)
                if self.header.index_version == '7.0':
                    records = index.size / 16
                else:
                    records = index.size / 20

                fileobj.seek(index.location, SEEK_SET)
                
                for _ in xrange(records):
                    self.DIR.append(DIR.parse(fileobj))                
                
                break
    