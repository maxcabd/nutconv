
import os, sys, array
import mmap, struct

from utils import (read_str, read_uint32, read_uint16, read_uint8)
from utils import (XFBIN, NUT)

# File paths
path = sys.argv[1]
head, tail = os.path.split(path)
outpath = path.split("/")[-1].split(tail)[-1]


# Bit masks
RGB_555 = (0x7C00, 0x3E0, 0x1F, 0x8000)
RGB_444 = (0xF00, 0xF0, 0xF, 0xF000)
RGB_565 = (0xF800, 0x7E0, 0x1F, 0x0)
RGB_888 = (0x00FF0000, 0x00FF00, 0xFF, 0xFF000000)


def xfbin_tex_export(): # Function that exports both DDS and NUT files from XFBIN files

# --Useful functions--
	def generate_chunk(chunk, data, size, mipmap, pixel, height, width): #Creates nested list chunk from NUT values
			chunk.append([])
			chunk[i].append([])
			chunk[i].extend([data])
			chunk[i].extend([[size, mipmap, pixel, height, width]])

	def set_header(pixel):
		if (pixel == 0):
			header = BC1_HEADER
		elif (pixel == 1):
			header = BC2_HEADER
		elif (pixel == 2):
			header = BC3_HEADER
		elif (pixel == 6):
			header = B5G5R5A1_HEADER
		elif (pixel == 7):
			header = B4G4R4A4_HEADER
		elif (pixel == 8):
			header = B5G6R5_HEADER
		elif (pixel == 14):
			header = B8G8R8A8_HEADER
		elif (pixel == 16):
			header = B8G8R8A8_HEADER
		return header		

	def compress_DXTn(chunk, pixel, header, data):
		if (pixel == 0 or pixel == 1 or pixel == 2):
			chunk[i][0] = array.array('u', header) + array.array('u', data)	
		if (pixel == 6 or pixel == 7 or pixel == 8):
			data = array.array('u', data)
			data.byteswap()
			chunk[i][0] = array.array('u', header) + data
		if (pixel == 16 or pixel == 14):
			data = array.array('l', data)
			data.byteswap()
			chunk[i][0] = array.array('l', header) + data
	
	def structDXT(compression):
		reserved1 = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
		return  (b'DDS ', 0x7C, 0x1007, height, width, data_size, 0x0, mipmap_count, *reserved1, 0x20, 0x4, compression, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0)

	def structDXT10(pitch, flags, bit, rgb):
		reserved1 = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
		return (b'DDS ', 0x7C, 0x2100F, height, width, pitch, 0x0, mipmap_count, *reserved1, 0x20, flags, 0x0, bit, *rgb, 0x401008, 0x0, 0x0, 0x0, 0x0)

	
	# --Read XFBIN file--
	with open(path, 'r+b') as xfbin:
		file = xfbin.read()
		mm = mmap.mmap(xfbin.fileno(), 0, access=mmap.ACCESS_READ)
		file_path_list = []
		xfbin.seek(28)
		XFBIN.Chunk_Type_Count = read_uint32(xfbin)
		xfbin.seek(32)
		XFBIN.Chunk_Type_Size = read_uint32(xfbin)
		xfbin.seek(XFBIN.HEADER_SIZE)
		xfbin.seek(36)
		XFBIN.File_Path_Count = read_uint32(xfbin)
		xfbin.seek(40)
		XFBIN.File_Path_size = read_uint32(xfbin)
		xfbin.seek(XFBIN.HEADER_SIZE + XFBIN.Chunk_Type_Size)
		
		for path_names in range(XFBIN.File_Path_Count):
			read_str(path_names, file_path_list, xfbin) 
		texture_names = [x for x in file_path_list if ".max" not in x and "celshade.nut" not in x] # Get names of Texture Chunks (ignore .max files and celshade texture)
		del texture_names[0]
		for i in range(len(texture_names)):
			texture_names[i] = texture_names[i].split('/')[-1:][0][:-4]
		
		# NTP3 offsets
		ntp3_count = file.count(NUT.NUT_MAGIC) 
		ntp3_offset = mm.find(NUT.NUT_MAGIC)
		ntp3_size_offset = ntp3_offset - 4
		
		def nut_dump():
			xfbin.seek(ntp3_offset + 24)
			NUT.data_size = read_uint32(xfbin)
			xfbin.seek(ntp3_offset + 28)
			NUT.header_size = read_uint16(xfbin)
			xfbin.seek(ntp3_offset + 33)
			NUT.mipmap_count = read_uint8(xfbin)
			xfbin.seek(ntp3_offset + 35)
			NUT.pixel_format = read_uint8(xfbin)
			xfbin.seek(ntp3_offset + 36)
			NUT.width = read_uint16(xfbin)
			xfbin.seek(ntp3_offset + 38)
			NUT.height = read_uint16(xfbin)	
			xfbin.seek(ntp3_offset + NUT.header_size + 16) #Seek to raw texture offset
			NUT.texture_data = xfbin.read(NUT.data_size) #Read and save raw NUT texture data

			xfbin.seek(ntp3_size_offset)
			nut_size = read_uint32(xfbin)
			xfbin.seek(ntp3_offset)
			nut = xfbin.read(nut_size)
			return NUT.texture_data, NUT.data_size, NUT.mipmap_count, NUT.pixel_format, NUT.height, NUT.width, nut

		# --Append Raw NUT Texture data and DDS header to Array-- // Will include alt texture data later
		dds_chunk = []
		nut_chunk = []
		for i in range(ntp3_count):
			nut_dump()
			texture_data, data_size, mipmap_count, pixel_format, height, width, nut = nut_dump()
			generate_chunk(dds_chunk, texture_data, data_size, mipmap_count, pixel_format, height, width)
			
			# string formats used for struct packing in one line
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
			B8G8R8A8_HEADER = struct.pack(dxt10_fstring, *structDXT10(0x800, 0x5B, 0x20, RGB_888))
			
			compress_DXTn(dds_chunk, pixel_format, set_header(pixel_format), texture_data) #Combines bytes for DDS file
			nut_chunk.append(nut)	
			ntp3_offset = mm.find(b'\x4e\x54\x50\x33', ntp3_offset + 1) #Find new occurence of 'NTP3' with each loop
		
		# --Create files and dump to folder--
		folder = outpath + '{} Textures'.format(tail[:-6]) + "\\"
		if not os.path.exists(folder):
			os.makedirs(folder)

		dds_names = [s + '.dds' for s in texture_names]
		for i, j in enumerate((dds_chunk)):
			with open(folder + dds_names[i], "wb") as dds:
				dds.write(dds_chunk[i][0])
				
		nut_names = [s + '.nut' for s in texture_names]
		for i, j in enumerate((nut_chunk)):
			with open(folder + nut_names[i], "wb") as nut:
				nut.write(nut_chunk[i])
		
		
