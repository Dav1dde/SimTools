from struct import pack, unpack
from io import BytesIO
from collections import namedtuple

FileHeader = namedtuple('FileHeader', ['compressed_size', 'magic', 'size'])

def decompress(data):
    if not hasattr(data, 'read'):
        data = BytesIO(data)
    
    header = unpack('<IH3B', data.read(9))
    compressed_size = header[0]
    magic = header[1]
    assert(magic == 0xfb10)
    size = (header[2] << 16 | header[3] << 8 | header[4] << 8)
    
    return (FileHeader(compressed_size, magic, size),
            _decompress(data, compressed_size-9, size))
    

def _decompress(fileobj, length, uncompressed_size):
    result = ''
    
    while length > 0 and len(result) < uncompressed_size:
        opcode, = unpack('<B', fileobj.read(1))
        length -= 1
        
        if opcode < 0x80:
            byte1, = unpack('<B', fileobj.read(1))
            length -= 1
            
            numplain = opcode & 0x03
            numcopy = ((opcode & 0x1c) >> 2) + 3
            offset = ((opcode & 0x60) << 3) + byte1 + 1
        elif opcode < 0xc0:
            byte1, byte2 = unpack('<2B', fileobj.read(2))
            length -= 2
            
            numplain = ((byte1 & 0xc0) >> 6) # & 0x03
            numcopy = (opcode & 0x3f) + 4
            offset = ((byte1 & 0x3f) << 8) + byte2 + 1
        elif opcode < 0xe0:
            byte1, byte2, byte3 = unpack('<3B', fileobj.read(3))
            length -= 3
            
            numplain = opcode & 0x03
            numcopy = ((opcode & 0x0c) << 6) + byte3 + 5
            #offset = (byte1 << 8) + byte2
            offset = ((opcode & 0x10) << 12) + (byte1 << 8) + byte2 + 1;
        elif opcode < 0xfc:
            numplain = ((opcode & 0x1f) << 2) + 4
            #numplain = (opcode - 0xdf) * 4
            numcopy = 0
            offset = 0
        else:
            numplain = opcode & 0x03
            #numplain = opcode - 0xfc
            numcopy = 0
            offset = 0
        
        if numplain:
            result += fileobj.read(numplain)
            length -= numplain
        
        if numcopy:
            fromoffset = len(result) - (offset) # offset = 0, means last character
                
            for i in xrange(numcopy):
                result += result[fromoffset+i]
        
    return result