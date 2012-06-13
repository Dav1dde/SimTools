from ctypes import CDLL, c_int, byref, create_string_buffer
import os.path

libsquish_path = os.path.join(os.path.split(os.path.abspath(__file__))[0], 'libsquishc.so')
libsquish = CDLL(libsquish_path)


DXT1 = 1 << 0 
DXT3 = 1 << 1 
DXT5 = 1 << 2 

COLOR_ITERATIVE_CLUSTER_FIT = 1 << 8    
COLOR_CLUSTER_FIT = 1 << 3    
COLOR_RANGE_FIT = 1 << 4
WEIGHT_COLOR_BY_ALPHA = 1 << 7


GetStorageRequirements = libsquish.GetStorageRequirements
GetStorageRequirements.argtypes = [c_int, c_int, c_int]
GetStorageRequirements.restype = c_int

def compress_image(rgba, width, height, flags):
    rgba = create_string_buffer(rgba)
    
    c = GetStorageRequirements(width, height, flags)
    buf = create_string_buffer(c)
    
    libsquish.CompressImage(byref(rgba), c_int(width), c_int(height), byref(buf), c_int(flags))
    
    return buffer.raw

def decompress_image(block, width, height, flags):
    block = create_string_buffer(block)
    
    c = width*height*4
    rgba = create_string_buffer(c)
    
    libsquish.DecompressImage(byref(rgba), c_int(width), c_int(height), byref(block), c_int(flags))
    
    return rgba.raw