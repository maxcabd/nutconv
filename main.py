#!/usr/bin/env python

"""NUT (Namco Universal Texture) file exporter and importer. Supports creation of NUT files from most DDS formats. Only exports NUT files for CyberConnect 2 games using .xfbin.
"""
__author__		= "Dei"
__date__ 		= '2022/03/01'

import sys
from xfbin_to_nut import xfbin_tex_export
from dds_to_nut import dds_to_nut
















if __name__ == '__main__':
	for arg in sys.argv[1:]:
		if arg.endswith('.xfbin'):
			xfbin_tex_export()
		elif arg.endswith('.dds'):
			dds_to_nut()
