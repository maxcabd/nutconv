import array, struct, io
from PIL import Image

from utils.xfbin_lib.xfbin.structure.nucc import NuccChunkTexture
from utils.xfbin_lib.xfbin.structure.nut import NutTexture

def nut2dds(nut: object) -> bytes:
	# Bit masks
	RGB_555 = (0x7C00, 0x3E0, 0x1F, 0x8000)
	RGB_444 = (0xF00, 0xF0, 0xF, 0xF000)
	RGB_565 = (0xF800, 0x7E0, 0x1F, 0x0)
	RGB_888 = (0xFF0000, 0xFF00, 0xFF, 0xFF000000)
    

    # Set the header for the DDS based on the NUT's pixel format
	def set_header(pixel_format):
		if (pixel_format == 0):
			header = BC1_HEADER

		elif (pixel_format == 1):
			header = BC2_HEADER

		elif (pixel_format == 2):
			header = BC3_HEADER

		elif (pixel_format == 6):
			header = B5G5R5A1_HEADER

		elif (pixel_format == 7):
			header = B4G4R4A4_HEADER

		elif (pixel_format == 8):
			header = B5G6R5_HEADER

		elif (pixel_format == 14):
			header = B8G8R8A8_HEADER

		elif (pixel_format == 17):
			header = B8G8R8A8_HEADER
		return header

    
    # Swap endian depending on compression
	def compress_DXTn(pixel_format, header, texture_data):
		if (pixel_format == 0 or pixel_format == 1 or pixel_format == 2):
			return array.array('u', header) + array.array('u', texture_data)	
		
		if (pixel_format == 6 or pixel_format == 7 or pixel_format == 8):
			texture_data = array.array('u', texture_data)
			texture_data.byteswap()
			return array.array('u', header) + texture_data
		
		if (pixel_format == 16 or pixel_format == 14 or pixel_format == 17):
			texture_data = array.array('l', texture_data)
			texture_data.byteswap()
			return array.array('l', header) + texture_data

	
	def structDXT(compression):
		reserved1 = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
		return  (b'DDS ', 0x7C, 0x1007, nut.height, nut.width, nut.data_size, 0x0, nut.mipmap_count, *reserved1, 0x20, 0x4, compression, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0)

	def structDXT10(pitch, flags, bit, rgb):
		reserved1 = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
		return (b'DDS ', 0x7C, 0x2100F, nut.height, nut.width, pitch, 0x0, nut.mipmap_count, *reserved1, 0x20, flags, 0x0, bit, *rgb, 0x401008, 0x0, 0x0, 0x0, 0x0)


	# String formats used for struct packing
	dxt_fstring = '4sllllllll11ll4sllllllllll' # DXT
	dxt10_fstring  = '4sllllllll11llllLLLLlllll' # DXT10
	
	# DXT Headers
	BC1_HEADER = struct.pack(dxt_fstring, *structDXT(b'DXT1'))
	BC2_HEADER = struct.pack(dxt_fstring, *structDXT(b'DXT3'))
	BC3_HEADER = struct.pack(dxt_fstring, *structDXT(b'DXT5'))

	# DXT10 headers
	B5G5R5A1_HEADER = struct.pack(dxt10_fstring, *structDXT10(0x400, 0x41, 0x10, RGB_555))
	B4G4R4A4_HEADER = struct.pack(dxt10_fstring, *structDXT10(0x400, 0x41, 0x10, RGB_444))
	B5G6R5_HEADER = struct.pack(dxt10_fstring, *structDXT10(0x400, 0x40, 0x10, RGB_565))
	B8G8R8A8_HEADER = struct.pack(dxt10_fstring, *structDXT10(0x800, 0x41, 0x20, RGB_888))
		
	# Create DDS object
	dds_file_object = compress_DXTn(nut.pixel_format, set_header(nut.pixel_format), nut.texture_data)


	return dds_file_object.tobytes()

def write_dds(texture, path):
	for i, tex in enumerate(texture.nut.textures):
		path = path.replace(f'{path.split("/")[-1]}' , f'{texture.name}_{i}.dds')
		with open(path, 'wb') as f:
			f.write(nut2dds(tex))
		f.close()

def write_png(texture: NuccChunkTexture, path):
	for i, tex in enumerate(texture.nut.textures):
		path = path.replace(f'{path.split("/")[-1]}' , f'{texture.name}_{i}.png')
		
		if tex.pixel_format == 0 or tex.pixel_format == 1 or tex.pixel_format == 2:
			dxt1 = nut2dds(tex)
			img = Image.open(io.BytesIO(dxt1)).save(path, 'PNG')
		elif tex.pixel_format == 6:
			texture_5551(tex.texture_data, tex.width, tex.height).save(path, 'PNG')
		elif tex.pixel_format == 7:
			texture_4444(tex.texture_data, tex.width, tex.height).save(path, 'PNG')
		elif tex.pixel_format == 8:
			texture_565(tex.texture_data, tex.width, tex.height).save(path, 'PNG')
		elif tex.pixel_format == 14 or tex.pixel_format == 17:
			texture_8888(tex.texture_data, tex.width, tex.height).save(path, 'PNG')


def texture_565(texture_data, width, height):
	texture_data = array.array('u', texture_data)
	texture_data.byteswap()

	return Image.frombytes('RGB', (width,height), texture_data.tobytes(), 'raw', 'BGR;16')

def texture_5551(texture_data, width, height):
	texture_data = array.array('u', texture_data)
	texture_data.byteswap()

	return Image.frombytes('RGBA', (width,height), texture_data.tobytes(), 'raw', 'BGRA;15')

def texture_4444(texture_data, width, height):
	texture_data = array.array('u', texture_data)
	texture_data.byteswap()

	image = Image.frombytes('RGBA', (width,height), texture_data.tobytes(), 'raw', 'RGBA;4B')
	r, g, b, a = image.split()
	return Image.merge('RGBA', (b, g, r, a))

def texture_8888(texture_data, width, height):
	image = Image.frombytes('RGBA', (width,height), texture_data, 'raw')	
	r, g, b, a = image.split()
	return Image.merge('RGBA', (g, b, a, r))
