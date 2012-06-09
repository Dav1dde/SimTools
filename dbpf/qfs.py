from os import SEEK_SET
from struct import pack, unpack

def decompress_file(fileobj, position):
    fileobj.seek(position, SEEK_SET)
    
    data = unpack('IH3B', fileobj.read(9))
    compressed_size = data[0]
    magic = hex(data[1])
    uncompressed_size = data[2] << 8*2 | data[3] << 8*1 | data[4] << 8*0
    
    return decompress_sc4(fileobj, compressed_size)
    

def decompress_sc4(fileobj, length):
    result = ''
    
    while length > 0:
        opcode, = unpack('B', fileobj.read(1))
        length -= 1
        
        if opcode < 0x80:
            byte1, = unpack('B', fileobj.read(1))
            length -= 1
            
            numplain = opcode & 0x03
            numcopy = ((opcode & 0x1c) >> 2) + 3
            offset = ((opcode & 0x60) << 3) + byte1 + 1
        elif opcode < 0xc0:
            byte1, byte2 = unpack('2B', fileobj.read(2))
            length -= 2
            
            numplain = ((byte1 & 0xc0) >> 6) # & 0x03
            numcopy = (opcode & 0x3f) + 4
            offset = ((byte1 & 0x3f) << 8) + byte2 + 1
        elif opcode < 0xe0:
            byte1, byte2, byte3 = unpack('3B', fileobj.read(3))
            length -= 3
            
            numplain = opcode & 0x03
            numcopy = ((opcode & 0x0c) << 6) + byte3 + 5
            offset = (byte1 << 8) + byte2
        elif opcode < 0xfc:
            #numplain = ((opcode & 0x1f) << 2) + 4
            numplain = (opcode - 0xdf) * 4
            numcopy = 0
            offset = 0
        else:
            #numplain = opcode & 0x03
            numplain = opcode - 0xfc
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

def decompress_sim(fileobj, length):
    result = ''
    
    while length > 0:
        opcode, = unpack('B', fileobj.read(1))
        length -= 1
        
        if opcode < 0x80:
            byte1, = unpack('B', fileobj.read(1))
            length -= 1
            
            numplain = opcode & 0x03
            numcopy = ((opcode & 0x1c) >> 2) + 3
            offset = ((opcode & 0x60) << 3) + byte1 + 1
        elif opcode < 0xc0:
            byte1, byte2 = unpack('2B', fileobj.read(2))
            length -= 2
            
            numplain = ((byte1 & 0xc0) >> 6) # & 0x03
            numcopy = (opcode & 0x3f) + 4
            offset = ((byte1 & 0x3f) << 8) + byte2 + 1
        elif opcode < 0xe0:
            byte1, byte2, byte3 = unpack('3B', fileobj.read(3))
            length -= 3
            
            numplain = opcode & 0x03
            numcopy = ((opcode & 0x0c) << 6) + byte3 + 5
            offset = ((opcode & 0x10) << 12) + (byte1 << 8) + byte2 + 1
        elif opcode < 0xfc:
            #numplain = ((opcode & 0x1f) << 2) + 4
            numplain = (opcode - 0xdf) * 4
            numcopy = 0
            offset = 0
        else:
            #numplain = opcode & 0x03
            numplain = opcode - 0xfc
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