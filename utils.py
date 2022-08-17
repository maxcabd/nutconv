
import struct



# --Class definitons--
class XFBIN:
	HEADER_SIZE = 68
	Chunk_Type_Count = 0
	Chunk_Type_Size = 0
	File_Path_Count = 0
	File_Path_Size = 0

class NUT:
	NUT_MAGIC = b'\x4e\x54\x50\x33'
	GIDX_MAGIC = b'\x47\x49\x44\x58'
	total_size = 0
	data_size = 0
	header_size = 0
	mipmaps = 0
	width = 0
	height = 0
	hash_id = 0
	texture_data = bytearray()

# -- Helper functions--
def read_str(string_table, chunk_table, file):
		
	string_table = []

	for char in iter(lambda: file.read(1).strip(), b'\x00'):
		char = char.decode("utf-8")
		string_table.append(char)
	string_table = [' ' if x == '' else x for x in string_table]
	string_table = ''.join(string_table)
	chunk_table.append(string_table)
	return string_table

def read_uint32(file): 
	
	result = 0
	
	for b in file.read(4):
		result = result * 256 + int(b)
	return result

def read_uint16(file): 
	
	result = 0
	
	for b in file.read(2):
		result = result * 256 + int(b)
	return result

def read_uint8(file): 
	
	result = 0
	
	for b in file.read(1):
		result = result * 256 + int(b)
	return result

def read_str32(file): 
	return struct.unpack('4s', file.read(4))[0].decode('utf-8')

def swap32(i):
    return struct.unpack("<I", struct.pack(">I", i))[0]

def swap16(i):
    return struct.unpack("<H", struct.pack(">H", i))[0]

def halve_mip(level):
		multiplier = 4
		
		if (level // 4 != multiplier):
			return level // 4
		else:
			return level
			
def calculate_mips(mipmaps):
	mip_levels = [1048576]
	
	if (mipmaps > 1):
		for i in range(mipmaps-1):
			mip_levels.append(halve_mip(mip_levels[i])) 
	return mip_levels

def calculate_mip_size(mipmaps):
	mip_levels = '{}I'.format(mipmaps)
	mip_levels_size = struct.calcsize(mip_levels)
	
	while (mip_levels_size % 0x10 != 0):
		mip_levels_size += 0x4
	return (mip_levels_size - struct.calcsize(mip_levels))


# Important functions

def export_files(buffer, filename, data, path):
			for i, j in enumerate((data)):
				with open(path + filename[i], "wb") as file:
					file.write(data[i])


# Struct Functions
def struct_NUT(total_size, data_size, mipmaps, add_mips, dds_count, pixel, width, height):
			pad6 = (0x0, 0x0, 0x0, 0x0, 0x0, 0x0)
			nut = (b'NTP3 ', 0x1, swap16(dds_count), 0x0, 0x0)
			mip_levels = [swap32(mip) for mip in calculate_mips(mipmaps)]
			header_size = 80

			if (mipmaps > 1):
				if add_mips == 0:
					header_size += (mipmaps * 4)
					total_size = data_size + header_size
					eXt = (swap32(total_size), 0x0, swap32(data_size), swap16(header_size), 0x0, mipmaps*256, pixel*256, width, height, *pad6, *mip_levels, b'eXt', swap32(0x20), swap32(0x10), 0x0, b'GIDX', swap32(0x10), 0x0, 0x0)
				else:
					header_size += (mipmaps * 4 + (add_mips* 4))
					total_size = data_size + header_size
					added_mips = []
					for _ in range(add_mips):
						added_mips.append(0)
					eXt = (swap32(total_size), 0x0, swap32(data_size), swap16(header_size), 0x0, mipmaps*256, pixel*256, width, height, *pad6, *mip_levels, *added_mips, b'eXt', swap32(0x20), swap32(0x10), 0x0, b'GIDX', swap32(0x10), 0x0, 0x0)	
			else:
				total_size = data_size + header_size
				eXt = (swap32(total_size), 0x0, swap32(data_size), swap16(header_size), 0x0, mipmaps*256, pixel*256, width, height, *pad6, b'eXt', swap32(0x20), swap32(0x10), 0x0, b'GIDX', swap32(0x10), 0x0, 0x0)		
			return nut, eXt # NUT Header bytes and GIDX header bytes
