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
            
            numplain = opcode & 0x03 # last two
            numcopy = ((opcode & 0x1c) >> 2) + 3 # XXX00 -> XXX+3; min=3, max=10
            offset = ((opcode & 0x60) << 3) + byte1 + 1 # 67 bit opcode, byte1 + 1; min=1, max=1024
        elif opcode < 0xc0:
            byte1, byte2 = unpack('<2B', fileobj.read(2))
            length -= 2
            
            numplain = ((byte1 & 0xc0) >> 6) # upper two bits
            numcopy = (opcode & 0x3f) + 4 # last 6 bits of opcode; min=4; max=67
            offset = ((byte1 & 0x3f) << 8) + byte2 + 1 # last 6 bits of byte 1, + byte2 +1; min=1, max=163848
        elif opcode < 0xe0: # last two = plain
            byte1, byte2, byte3 = unpack('<3B', fileobj.read(3))
            length -= 3
            
            numplain = opcode & 0x03 # last two
            numcopy = ((opcode & 0x0c) << 6) + byte3 + 5 # XX00 -> XXbyte3+5; min=5, max=1028
            offset = ((opcode & 0x10) << 12) + (byte1 << 8) + byte2 + 1 # min=1, max=131072
        elif opcode < 0xfc: # lower 3 bits + 4
            numplain = ((opcode & 0x1f) << 2) + 4
            #numplain = (opcode - 0xdf) * 4
            numcopy = 0
            offset = 0
        else: # last two bits
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


def try_compress(data):
    try:
        compressed = compress(data)
    except ValueError:
        compressed = None
        
    if compressed is None or len(compressed) >= len(data):
        return False, data
    else:
        return True, compressed
        

def compress(data):
    if hasattr(data, 'read'):
        data = data.read()
    
    compressed = _compress(data)
    compressed_size = len(compressed) + 9 # 9 = size of header
    magic = 0xfb10
    size = len(data) & 0xffffff
    header = pack('<IH3B', compressed_size, magic,
                  (size & 0xff0000) >> 16, (size & 0x00ff00) >> 8, size & 0x0000ff)
    
    return ''.join([header, compressed])

def _compress(data):
    # lz77 algorithm based on (14.6.2012):
    # https://github.com/olle/lz77-kit/blob/master/src/main/python/lz77.py
    # which is licensed under MIT
    
    result = ''
    
    buf = ''
    
    min_match_length = 5
    max_string_length = 1028
    window_length = 1200
    best_match_length = 0
    
    pos = 0
    end = len(data)
    

    while pos < end:
        match_length = min_match_length
        search_start = max(pos - window_length, 0)
        best_match_distance = max_string_length
        best_match_length = 0
        
        found_match = False
        
        while (search_start + match_length) < pos:
            m1 = data[search_start:search_start + match_length]
            m2 = data[pos:pos + match_length]
            
            is_valid_match = (m1 == m2 and match_length < max_string_length)
            
            if is_valid_match:
                match_length += 1
                found_match = True
            else:
                real_match_length = match_length - 1
                
                if found_match and real_match_length > best_match_length:
                    best_match_distance = pos - search_start - real_match_length
                    best_match_length = real_match_length
                    
                match_length = min_match_length
                search_start += 1
                found_match = False
            
        new_compressed = ''
        if best_match_length:
            if buf:
                new_compressed = ''.join(_output_plain(buf))
                buf = ''
            
            new_compressed += ''.join(_output_offset(best_match_distance+best_match_length, best_match_length))
            pos += best_match_length
        else:
            buf += data[pos]
            pos += 1
        
        result += new_compressed
    
    result += ''.join(_output_plain(buf))
    
    return result


def _output_plain(buf):
    sizes = [28, 24, 20, 16, 12, 8, 4, 3, 2, 1]
    
    while len(buf):
        for size in sizes:
            if size <= len(buf):
                data = buf[:size]
                if size < 4:
                    yield ''.join([pack('<B', 0xfc + len(data)), data])
                else:
                    yield ''.join([pack('<B', 0xe0 | ((len(data) - 4) >> 2)), data])                
                
                buf = buf[size:]
                break
    
def _output_offset(offset, length):
    if 2 < length <= 10 and offset <= 1024:
        lower = (length - 3) << 2
        
        x = offset - 1
        byte1 = x & 0xff
        upper = x >> 8
        
        opcode = (upper << 5) | lower
        opcode = pack('<B', opcode)
        bytes = pack('<B', byte1)        
    elif 3 < length <= 67 and offset <= 163848:
        opcode = (length - 4) & 0x3f | 0x80
        opcode = pack('<B', opcode)
        
        x = offset - 1
        byte2 = x & 0xff
        byte1 = (x >> 8) & 0x3f
        bytes = pack('<BB', byte1, byte2)
    elif 4 < length <= 1028 and offset <= 131072:
        x = length - 5
        byte3 = x & 0xff
        lower = (x >> 8) & 0x0c
        
        x = offset - 1
        byte2 = x & 0xff
        byte1 = (x >> 8) & 0xff
        upper = (x >> 16) & 0x10
        
        opcode = upper | lower | 0xc0
        opcode = pack('<B', opcode)
        bytes = pack('<BBB', byte1, byte2, byte3)        
    else:
        raise ValueError('failed to compress data') # TODO: FIX ME
    
    yield ''.join([opcode, bytes])



if __name__ == '__main__':
    data = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz123456789abcefghijklmno'
    print data, len(data)
    compressed = _compress(data)
    print repr(compressed), len(compressed)
    decompressed = _decompress(BytesIO(compressed), len(compressed), len(data))
    print decompressed
    assert(data == decompressed)
    
    c = compress(data)
    print repr(c)
    header, uc = decompress(c)
    print uc
    print header
    assert(data == uc)
    