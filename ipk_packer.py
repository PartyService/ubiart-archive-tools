#
# https://github.com/PartyService/Ubiart-Archive-Tools
#
# UbiArt Archive Tools (IPK) is an useful scripts to extract or pack an .ipk
# 
# This Script Made Possible by Party Team, just gemer, Planedec50, leamsii, XpoZed, InvoxiPlayGames
#

import numpy as np
import os
import sys
import struct
import zlib, lzma, re
import json, math
from pathlib import PureWindowsPath, Path

ENDIANNESS = '>'  # Big endian
STRUCT_SIGNS = {
    1: 'c',
    2: 'H',
    4: 'I',
    8: 'Q'
}

# Define a basic IPK file header
IPK_HEADER = {
    'magic': 1357648570,      # Decimal integer value for b'\x50\xEC\x12\xBA'
    'version': 0,             # The Version of .ipks
    'platformsupported': 8,   # idk what this var is for
    'base_offset': 0,         # Initial raw file offset value (set to 0)
    'num_files': 0,           # Initialize the count of files (set to 0)
    'compressed': 0,          # is whole ipk compressed maybe??
    'binaryscene': 0,         # Set to 0
    'binarylogic': 0,         # Bundlelogic maybe??
    'datasignature': 0,       # Maybe For crc32 checksum?
    'enginesignature': 0,     # Game ID, to identify the games
    'engineversion': 0,       # Engine Version Of The game
    'num_files2': 0,          # idk why it's doubled?
}

def shifter(a, b, c):
    d = np.uint32(0)
    a = np.uint32((a - b - c) ^ (c >> 0xd))
    b = np.uint32((b - a - c) ^ (a << 0x8))
    c = np.uint32((c - a - b) ^ (b >> 0xd))
    a = np.uint32((a - c - b) ^ (c >> 0xc))
    d = np.uint32((b - a - c) ^ (a << 0x10))
    c = np.uint32((c - a - d) ^ (d >> 0x5))
    a = np.uint32((a - c - d) ^ (c >> 0x3))
    b = np.uint32((d - a - c) ^ (a << 0xa))
    c = np.uint32((c - a - b) ^ (b >> 0xf))
    return a, b, c

def crc(data):
    np.seterr(all="ignore")
    a = np.uint32(0x9E3779B9)
    b = np.uint32(0x9E3779B9)
    c = np.uint32(0)
    length = len(data)

    if length > 0xc:
        i = 0
        while i < math.floor(length / 0xc):
            a += np.uint32((((((data[i * 0xc + 0x3] << 8) + data[i * 0xc + 0x2]) << 8) + data[i * 0xc + 0x1]) << 8) + data[i * 0xc])
            b += np.uint32((((((data[i * 0xc + 0x7] << 8) + data[i * 0xc + 0x6]) << 8) + data[i * 0xc + 0x5]) << 8) + data[i * 0xc + 0x4])
            c += np.uint32((((((data[i * 0xc + 0xb] << 8) + data[i * 0xc + 0xa]) << 8) + data[i * 0xc + 0x9]) << 8) + data[i * 0xc + 0x8])
            i += 1
            a, b, c = shifter(a, b, c)

    c += np.uint32(length)
    i = np.uint32(length - (length % 0xc))

    decide = (length % 0xc) - 1
    if decide >= 0xa:
        c += np.uint32(data[i + 0xa] << 0x18)
    if decide >= 0x9:
        c += np.uint32(data[i + 0x9] << 0x10)
    if decide >= 0x8:
        c += np.uint32(data[i + 0x8] << 0x8)
    if decide >= 0x7:
        b += np.uint32(data[i + 0x7] << 0x18)
    if decide >= 0x6:
        b += np.uint32(data[i + 0x6] << 0x10)
    if decide >= 0x5:
        b += np.uint32(data[i + 0x5] << 0x8)
    if decide >= 0x4:
        b += np.uint32(data[i + 0x4])
    if decide >= 0x3:
        a += np.uint32(data[i + 0x3] << 0x18)
    if decide >= 0x2:
        a += np.uint32(data[i + 0x2] << 0x10)
    if decide >= 0x1:
        a += np.uint32(data[i + 0x1] << 0x8)
    if decide >= 0x0:
        a += np.uint32(data[i + 0x0])

    a, b, c = shifter(a, b, c)

    return int(np.uint32(c))

def _exit(msg):
    print(msg)
    print("Exiting..")
    sys.exit(-1)

def pack(target_folder, output_ipk, config_data):
    # Collect file information
    file_info = []
    raw_data = b''
    offset = 0  # Initial offset value
    num_files = 0  # Initialize the count of files

    for root, _, files in os.walk(target_folder):
        for file_name in files:
            full_path = os.path.normpath(os.path.join(root, file_name)) #Normalize path to avoid script bruken
            rel_path = os.path.normpath(os.path.relpath(root, target_folder))  # Relative path without filename
            file_size = os.path.getsize(full_path)
            last_modified = int(os.path.getmtime(full_path))

            # If getmtime returns 0, use getctime instead
            if last_modified == 0:
                last_modified = int(os.path.getctime(full_path))

            if os.path.sep == '\\':
                  rel_path = PureWindowsPath(rel_path).as_posix()

            if not rel_path.endswith('/') and rel_path != '':
                rel_path += '/'

            if rel_path == './':
                rel_path = ''

            if config_data.get('switchTitle', default_config['switchTitle']) == True:
                tmp_path = rel_path
                tmp_name = file_name
                file_name = tmp_path
                rel_path = tmp_name
                
            with open(full_path, 'rb') as file:
                readedFile = file.read()
                if any(file_name.endswith(substring) for substring in config_data.get('compress', default_config['compress'])):
                    if config_data.get('method', default_config['method']) == "lzma":
                        print(f"lzma: Compressing: {file_name}  ", end="\r")
                        file_data = lzma.compress(readedFile)
                    else: ## Newer IPK's uses LZMA for compression, old one uses zlib, theyre both working in new version
                        print(f"zlib: Compressing: {file_name}  ", end="\r")
                        file_data = zlib.compress(readedFile)
                    origin_size = len(readedFile)
                    compressed_size = len(file_data)
                else:
                    file_data = readedFile
                    origin_size = len(readedFile)
                    compressed_size = 0
                raw_data += file_data

            flags = 0
            if file_name.endswith('.ckd'): 
                flags = 2
            # Calculate name and path sizes
            name_size = len(file_name.encode())
            path_size = len(rel_path.encode())
            crcpath = f'{rel_path}{file_name}'.upper()
            stringID = crc(crcpath.encode())

            file_info.append({
                'file_name': file_name.encode(),
                'path_name': rel_path.encode(),
                'file_size': origin_size,
                'compressed_size': compressed_size,
                'time_stamp': last_modified,
                'offset': offset,
                'name_size': name_size,
                'path_size': path_size,
                'checksum': stringID,
                'flags': flags
            })


            # Update offset for the next file
            offset += len(file_data)
            num_files += 1  # Increment the count of files

    # Calculate the total size of header and file info
    header_size = 0
    for k, v in IPK_HEADER.items():
        header_size += 4  # Each value is represented as 4 bytes

    file_info_size = 0
    for file_data in file_info:
        file_info_size += 4  # Size of num_offset
        file_info_size += 4  # Size of file_size
        file_info_size += 4  # Size of compressed_size
        file_info_size += 8  # Size of time_stamp
        file_info_size += 8  # Size of offset
        file_info_size += 4  # Size of name_size
        file_info_size += len(file_data['file_name'])
        file_info_size += 4  # Size of path_size
        file_info_size += len(file_data['path_name'])
        file_info_size += 4  # Size of checksum
        file_info_size += 4  # Size of flag

    # Update base_offset in the header
    IPK_HEADER['base_offset'] = header_size + file_info_size
    # Update header information with the correct number of files
    IPK_HEADER['num_files'] = num_files
    IPK_HEADER['num_files2'] = num_files
    # Use variables from config.json
    IPK_HEADER['version'] = config_data.get('version', default_config['version'])
    IPK_HEADER['enginesignature'] = config_data.get('gameid', default_config['gameid'])
    IPK_HEADER['engineversion'] = config_data.get('engineversion', default_config['engineversion'])
    

    with open(output_ipk, 'wb') as ipk_file:
        # Write the header
        for k, v in IPK_HEADER.items():
            ipk_file.write(struct.pack(ENDIANNESS + STRUCT_SIGNS[4], v))

        # Write file chunks
        for file_data in file_info:
            ipk_file.write(struct.pack(ENDIANNESS + STRUCT_SIGNS[4], 1))  # num_offset, set to 1
            ipk_file.write(struct.pack(ENDIANNESS + STRUCT_SIGNS[4], file_data['file_size']))
            ipk_file.write(struct.pack(ENDIANNESS + STRUCT_SIGNS[4], file_data['compressed_size']))  # z_size, set to the same as size
            ipk_file.write(struct.pack(ENDIANNESS + STRUCT_SIGNS[8], file_data['time_stamp']))
            ipk_file.write(struct.pack(ENDIANNESS + STRUCT_SIGNS[8], file_data['offset']))
            ipk_file.write(struct.pack(ENDIANNESS + STRUCT_SIGNS[4], file_data['name_size']))
            ipk_file.write(file_data['file_name'])
            ipk_file.write(struct.pack(ENDIANNESS + STRUCT_SIGNS[4], file_data['path_size']))
            ipk_file.write(file_data['path_name'])
            ipk_file.write(struct.pack(ENDIANNESS + STRUCT_SIGNS[4], file_data['checksum']))  # checksum, set to 0
            ipk_file.write(struct.pack(ENDIANNESS + STRUCT_SIGNS[4], file_data['flags']))  # flag, set to 0

        # Write the raw data at the end of the file
        ipk_file.write(raw_data)

    print(f"\nLog: Packing completed to {output_ipk}.")

# Get the output IPK file name
default_config = {
    'version': 5,
    'gameid': 490359856,
    'engineversion': 253653,
    'switchTitle': False,
    'compress': [ '.dtape.ckd', '.fx.fxb', '.m3d.ckd', '.png.ckd', '.tga.ckd' ],
    'method': 'zlib'
}


# Check if the config.json file exists
config_file_path = os.path.join( os.path.dirname( __file__ ), 'config.json')
if not os.path.exists(config_file_path):
    print("Warning: config.json file not found. Creating a new one with default configuration.")
    config_data = default_config
    # Write the default configuration to a new config.json file
    with open(config_file_path, 'w') as config_file:
        json.dump(default_config, config_file, indent=4)
else:
    # Read and parse the config.json file
    with open(config_file_path, 'r') as config_file:
        config_data = json.load(config_file)

# Check if the proper arguments were given
args = sys.argv
if len(args) != 3:
    _exit("Error: Please specify a target folder to pack and the output")

# Check if the folder exists
target_folder = Path(args[1])
if not target_folder.is_dir():
    _exit(f"Error: The folder '{target_folder}' does not exist or is not a directory!")
        
output_ipk = args[2]

# Pack the folder
pack(target_folder, output_ipk, config_data)