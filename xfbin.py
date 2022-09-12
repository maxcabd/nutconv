from dds import DDS_Header
from utils.xfbin_lib.xfbin import *
from utils.PyBinaryReader.binary_reader import BinaryReader
from utils.xfbin_lib.xfbin.structure.nut import Nut, NutTexture
from utils.xfbin_lib.xfbin.structure.br.br_nut import *
from array import array
from brDDS import BrDDS

#read xfbin then store in a list    
xfbins = list()
textures = list()

def read_xfbin(xfbin_path):
    xfbin = xfbin_reader.read_xfbin(xfbin_path)
    xfbins.append(xfbin)
    

def write_xfbin(xfbin, xfbin_path):
    print("write_xfbin")
    xfbin_writer.write_xfbin_to_path(xfbin, xfbin_path)


def write_nut(texture, nut_path):
    nut_path = f'{nut_path}//{texture.name}.nut'
    nut: Nut = texture.nut
    br = BinaryReader(endianness=Endian.BIG)
    br.write_struct(BrNut(), nut)
    with open(nut_path, 'wb') as f:
        f.write(br.buffer())
    print(f'Wrote {nut_path}')

class CopiedTextures:
    c_tex = list()
    def __init__(self, texture: NuccChunkTexture):
        self.name = texture.name
        self.filePath = texture.filePath
        self.nut = texture.nut

def create_texture_chunk(self):
    tex = NuccChunkTexture(CopiedTextures(self).filePath, CopiedTextures(self).name)
    tex.nut = CopiedTextures(self).nut
    CopiedTextures(self).c_tex.append(tex)
    return tex

def texture_from_file(path, name):
    with open(path, 'rb') as f:
        data = f.read()
    with BinaryReader(data, Endian.BIG) as br:
        nut: BrNut = br.read_struct(BrNut)

    tex = NuccChunkTexture(f'c/chr/tex/{name}', f'{name[:-4]}')
    tex.nut = nut

    return tex