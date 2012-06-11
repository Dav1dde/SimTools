from collections import namedtuple

from simtools.file import File, XMLFile, S3DFile, ImageFile, FSHFile


T = namedtuple('T', ['type', 'description', 'cls'])


TID = {0xbadb57f1 : T('S3D', 'SimGlide 3D Model', S3DFile),
       0x1abe787d : T('FSH', 'Texture File', FSHFile),
       0x0986135E : T('FSH', 'Base and Overlay Lot Textures', FSHFile),
       0x1ABE787D : T('FSH', 'Transit Textures/Buildings/Bridges/Misc', FSHFile),
       0x2BC2759A : T('FSH', 'Transit Network Shadows (Masks)', FSHFile),
       0x891B0E1A : T('FSH', 'Terrain and Foundation', FSHFile),
       0x49A593E7 : T('FSH', 'Animation Sprites (Non Props)', FSHFile),
       0x2A2458F9 : T('FSH', 'Animation Sprites (Props)', FSHFile),
       
       # own assumptions
       0x5ad0e187 : T('S3D', 'SimGlide 3D Model', S3DFile),
       0x7ab50e44 : T('FSH', 'Texture File', FSHFile),
       0x88777601 : T('XML', 'XML File', XMLFile),
       0x74807101 : T('JPEG', 'Compressed Image File', ImageFile),
       0x74807102 : T('JPEG', 'Compressed Image File', ImageFile),
       0x66778001 : T('BMP', 'Bitmap Image File', ImageFile),
       0x66778002 : T('BMP', 'Bitmap Image File', ImageFile)}

# ltext1 typeid: 6534284a

def magic_index(index):
    if index.type_id in TID:
        return TID[index.type_id]
    else:
        return T('data', 'can be everything', File)