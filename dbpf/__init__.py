from dbpf.header import Header, Hole, index, dir
from os import SEEK_SET

class DBPF(object):
    def __init__(self, fileobj):
        self._fileobj = fileobj
    
        self._header = None
        self._indices = list()
        self._holes = list()
        
        self._parse_file()
        
        self._iter = iter(self._indices)
    
    @classmethod
    def open(cls, path):
        return cls(open(path, 'rb'))
    
    def close(self):
        self._fileobj.close()

    def _parse_file(self):
        self._header = Header.parse(self._fileobj)
        
        if not self._header.magic == 'DBPF':
            raise ValueError('This is not a valid DBPF file.')
        if not self._header.version == '1.0':
            raise ValueError('DBPF Version not supported')
        
        self._extract_indices()
        self._extract_holes()
        self._mark_compressed()
    
    def _extract_indices(self):
        if self._header.index_count >= 1:
            Index = index(self._header.index_version)
            
            self._fileobj.seek(self._header.index_offset, SEEK_SET)
            
            for _ in xrange(self._header.index_count):
                self._indices.append(Index.parse(self._fileobj))
            
            if not self._fileobj.tell() == (self._header.index_offset + self._header.index_size):
                raise ValueError('incorrect amount of data read, file to small?')
    
    def _extract_holes(self):
        if self._header.holes_count >= 1:
            self._fileobj.seek(self._header.holes_offset, SEEK_SET)
            
            for _ in xrange(self._header.holes_count):
                self._holes.append(Hole.parse(self._fileobj))
                
            if not self._fileobj.tell() == (self._header.holes_offset + self._header.holes_size):
                raise ValueError('incorrect amount of data read, file to small?')
            
    def _mark_compressed(self):
        for index in self._indices:
            if index.type_id == 0xe86b1eef:
                DIR = dir(self._header.index_version)
                if self._header.index_version == '7.0':
                    records = index.size / 16
                else:
                    records = index.size / 20

                self._fileobj.seek(index.location, SEEK_SET)
                
                indices = self._indices[:]
                for _ in xrange(records):
                    parsed = DIR.parse(self._fileobj)
                    
                    for index in indices:
                        if parsed.equals_index(index):
                            index.compressed = True
                            indices.remove(index)           
                            
    def __enter__(self):
        return self
    
    def __iter__(self):
        self._iter = iter(self._indices)
        return self._iter
    
    def __next__(self):
        return next(self._iter)
    
    next = __next__
    
    def __exit__(self, type, value, traceback):
        self.close()
