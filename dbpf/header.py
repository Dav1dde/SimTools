from struct import Struct
from collections import namedtuple

HEADER_STRUCT = Struct('<4s17i24s')
HEADER_SIZE = HEADER_STRUCT.size

HeaderType = namedtuple('HeaderType', ['magic',
                                       'version_major', 'version_minor',
                                       'user_version_major', 'user_version_minor',
                                       'flags',
                                       'ctime', 'mtime',
                                       'index_version_major',
                                       'index_count', 'index_offset', 'index_size',
                                       'holes_count', 'holes_offset', 'holes_size',
                                       'index_version_minor',
                                       'index_offfset2',
                                       'unknown',
                                       'reserved'])

class Header(HeaderType):
    @property
    def version(self):
        return u'.'.join([unicode(self.version_major), unicode(self.version_minor)])
    
    @property
    def user_version(self):
        return u'.'.join([unicode(self.user_version_major), unicode(self.user_version_minor)])
    
    @staticmethod
    def parse(cls, fileobj):
        '''takes an opened file or file-like-object and returns a 
        parsed Header class'''
        header = fileobj.read(HEADER_SIZE)
        
        return cls._make(HEADER_STRUCT.unpack(header))