from os import SEEK_SET

from simtools.dbpf import Header, Hole, index, dir
from simtools.util import enforce



class DBPF(object):
    def __init__(self, fileobj):
        self._fileobj = fileobj
    
        self.header = None
        self.indices = list()
        self.holes = list()
        
        self._parse_file()
        
        self._iter = iter(self.indices)
    
    @classmethod
    def open(cls, path):
        return cls(open(path, 'rb'))
    
    def close(self):
        self._fileobj.close()

    def _parse_file(self):
        self.header = Header.parse(self._fileobj)
        
        enforce(self.header.magic == 'DBPF', ValueError, 'This is not a valid DBPF file.')
        enforce(self.header.version == '1.0', ValueError, 'DBPF Version not supported')
        
        self._extract_indices()
        self._extract_holes()
        self._mark_compressed()
    
    def _extract_indices(self):
        if self.header.index_count >= 1:
            Index = index(self.header.index_version)
            
            self._fileobj.seek(self.header.index_offset, SEEK_SET)
            
            for _ in xrange(self.header.index_count):
                self.indices.append(Index.parse(self._fileobj))
            
            if not self._fileobj.tell() == (self.header.index_offset + self.header.index_size):
                raise ValueError('incorrect amount of data read, file to small?')
    
    def _extract_holes(self):
        if self.header.holes_count >= 1:
            self._fileobj.seek(self.header.holes_offset, SEEK_SET)
            
            for _ in xrange(self.header.holes_count):
                self.holes.append(Hole.parse(self._fileobj))
                
            if not self._fileobj.tell() == (self.header.holes_offset + self.header.holes_size):
                raise ValueError('incorrect amount of data read, file to small?')
            
    def _mark_compressed(self):
        for index in self.indices:
            if index.type_id == 0xe86b1eef:
                DIR = dir(self.header.index_version)
                if self.header.index_version == '7.0':
                    records = index.size / 16
                else:
                    records = index.size / 20

                self._fileobj.seek(index.location, SEEK_SET)
                
                indices = self.indices[:]
                for _ in xrange(records):
                    parsed = DIR.parse(self._fileobj)
                    
                    for index in indices:
                        if parsed.equals_index(index):
                            index.compressed = True
                            indices.remove(index)           
                            
    def __enter__(self):
        return self
    
    def __iter__(self):
        self._iter = iter(self.indices)
        return self._iter
    
    def __next__(self):
        return next(self._iter)
    
    next = __next__
    
    def __exit__(self, type, value, traceback):
        self.close()
