from dbpf.header import Header, index
from os import SEEK_SET


class DBPF(object):
    def __init__(self, file=None, ignore_magic=False):
        self.ignore_magic = ignore_magic
        
        self.header = None
        self.indices = []
        self.holes = []
        
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
    
        if self.header.index_count >= 1:
            Index = index(self.header.index_version)
            
            fileobj.seek(self.header.index_offset, SEEK_SET)
            for i in xrange(self.header.index_count):
                self.indices.append(Index.parse(fileobj))