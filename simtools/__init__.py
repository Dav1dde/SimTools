from os import SEEK_SET
from random import randint
from itertools import izip

from simtools import dbpf
from simtools.util import enforce

group_id_factory = lambda: randint(0x10000000, 0xffffffff)

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
        self.header = dbpf.Header.parse(self._fileobj)

        enforce(self.header.magic == 'DBPF', ValueError, 'This is not a valid DBPF file.')
        enforce(self.header.version == '1.0', ValueError, 'DBPF Version not supported')
        
        self._extract_indices()
        self._extract_holes()
        self._mark_compressed()
    
    def _extract_indices(self):
        if self.header.index_count >= 1:
            Index = dbpf.index(self.header.index_version)
            
            self._fileobj.seek(self.header.index_offset, SEEK_SET)
            
            for _ in xrange(self.header.index_count):
                self.indices.append(Index.parse(self._fileobj))
            
            if not self._fileobj.tell() == (self.header.index_offset + self.header.index_size):
                raise ValueError('incorrect amount of data read, file to small?')
    
    def _extract_holes(self):
        if self.header.holes_count >= 1:
            self._fileobj.seek(self.header.holes_offset, SEEK_SET)
            
            for _ in xrange(self.header.holes_count):
                self.holes.append(dbpf.Hole.parse(self._fileobj))
                
            if not self._fileobj.tell() == (self.header.holes_offset + self.header.holes_size):
                raise ValueError('incorrect amount of data read, file to small?')
            
    def _mark_compressed(self):
        for index in self.indices:
            if index.type_id == 0xe86b1eef:
                DIR = dbpf.dir(self.header.index_version)
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


    def save(self, path):
        version = self.header.index_version
        DIR = dbpf.dir(version)
        Index = dbpf.index(version)
        
        files = list()
        dirs = list()
        indices = list()
        compressed_files = 0
        for index in self.indices:
            if index.type_id == 0xe86b1eef:
                continue
            
            indices.append(index)
            
            compressed, data = index.dump_file()
            
            if compressed:
                compressed_files += 1
                args = index._data.copy()
                del args['location']
                if not index._file is None:
                    args['size'] = len(index._file.raw())
                print index, args.values()
                dirs.append(DIR(*args.values()).raw())
            files.append(data)
        
        indices_data = list() 
       
        offset = dbpf.Header._struct.size
        offset += len(indices)*Index._struct.size
        offset += DIR._struct.size if compressed_files > 0 else 0
        
        for index, file in izip(indices, files):
            index.location = offset
            indices_data.append(index.raw())
            
            offset += len(file)
        
        if compressed_files > 0:
            if version == '7.0':
                size = 16
                indices_data.append(Index(0xe86b1eef, 0xe86b1eef,
                                          0x286b1f03, offset,
                                          compressed_files*size).raw())
            else:
                size = 20
                indices_data.append(Index(0xe86b1eef, 0xe86b1eef, 0x286b1f03,
                                          0x286b1f03, offset,
                                          compressed_files*size).raw())
            
        self.header.index_count = len(indices_data)
        self.header.index_offset = 96
        self.header.index_size = len(indices_data)*Index._struct.size
        self.header.holes_count = 0
        self.header.holes_offset = 0
        self.header.holes_size = 0

        indices_data = ''.join(indices_data)
        
        with open(path, 'w') as f:
            f.write(self.header.raw())
            f.write(indices_data)
            
            for file in files:
                f.write(file)
            
            f.write(''.join(dirs))
        
                            
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
