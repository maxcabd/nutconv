
import struct, os, array, sys

from utils import* #read_uint32, read_uint16, read_uint8, read_str32, struct_NUT

# DXGI Formats 
DXGI_555 = 0x56
DXGI_444 = 0x41
DXGI_565 = 0x40
DXGI_888 = 0x5B

	
def dds_to_nut():
	
	
	def get_data_dds(file):
		with open(file, 'rb') as dds:
				
				data_size = os.path.getsize(file) - 0x80
				total_size = data_size + 0x50
				dds.seek(0x0D)
				height = read_uint16(dds)
				dds.seek(0x11)
				width = read_uint16(dds)
				dds.seek(0x1C)
				mipmaps = read_uint8(dds)
				
				dds.seek(0x4D)
				flags = read_uint32(dds)
				
				dds.seek(0x5B)
				r_bitmask = read_uint32(dds)
				if (flags == DXGI_555 and r_bitmask == 0x7C00):
					pixel_format = 0x6
				elif (flags == DXGI_444 and r_bitmask == 0xF00):
					pixel_format = 0x7
				elif (flags == DXGI_565):
					pixel_format = 0x8
				elif (flags == DXGI_888):
					pixel_format = 0x10

				dds.seek(0x54)
				compression_type = read_str32(dds)
				if (compression_type == ''):
					pass
				elif compression_type == 'DXT1':
					pixel_format = 0x0
				elif compression_type == 'DXT3':
					pixel_format = 0x1
				elif compression_type == 'DXT5':
					pixel_format = 0x2

				dds.seek(0x80)
				texture_data = dds.read(data_size)

				if (pixel_format == 0x6 or pixel_format == 0x7 or pixel_format == 0x8):
					texture_data = array.array('u', texture_data)
					texture_data.byteswap()
				elif (pixel_format == 0x10):
					texture_data = array.array('l', texture_data)
					texture_data.byteswap()
				else:
					texture_data = array.array('u', texture_data)
					
				
				nut_header, eXt_header = struct_NUT(total_size, data_size, mipmaps, len(sys.argv)-1, pixel_format, width, height)
				nut_fstring = '4sHHII'
				nut_header = struct.pack(nut_fstring, *nut_header)
				if (mipmaps > 1):
					eXt_fstring = 'III HH hH HH 6I {}I 3s III 4s III'.format(mipmaps)
				else:
					eXt_fstring = 'III HH hH HH 6I 3s III 4s III'
				eXt_header = struct.pack(eXt_fstring, *eXt_header)
				nut_texture = eXt_header + texture_data
				return nut_header, nut_texture

	gidx_chunk = [get_data_dds(file) for file in sys.argv[1:]]

	nut_file = gidx_chunk[0][0]
	for i in range(len(sys.argv)-1):
		nut_file += gidx_chunk[i][1]

	head, tail = os.path.split(sys.argv[1])
	outpath = sys.argv[1].split("/")[-1].split(tail)[-1]
	with open(outpath + tail[:-4] + '.nut', "wb") as nut:
			nut.write(nut_file)




