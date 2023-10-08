#
# https://github.com/PartyService/Ubiart-Archive-Tools
#
# UbiArt Archive Tools (IPK) is an useful scripts to extract or pack an .ipk
# 
# This Script Made Possible by nicholas, just gemer, Planedec50, leamsii, ibratabian17, XpoZed
#

import os
import sys
import struct
import zlib, lzma
import json
from pathlib import Path
from time import time, sleep

ENDIANNESS = '>'  # Big endian
STRUCT_SIGNS = {
    1: 'c',
    2: 'H',
    4: 'I',
    8: 'Q'
}

# Define a basic IPK file header
IPK_HEADER = {
    'magic': 1357648570,       # Decimal integer value for b'\x50\xEC\x12\xBA'
    'version': 5,             # Decimal integer value for b'\x00\x00\x00\x05'
    'platformsupported': 0,   # Set to 0
    'base_offset': 0,         # Initial offset value (set to 0)
    'num_files': 0,           # Initialize the count of files (set to 0)
    'compressed': 0,            # Set to 0
    'binaryscene': 0,             # Set to 0
    'binarylogic': 0,                # Bundlelogic maybe??
    'datasignature': 0,              #
    'enginesignature': 490359856,    # Let's just say this is just dance 2017
    'engineversion': 253653,         #This is the engine version used by JD17
    'num_files2': 0,          #idk why it's doubled?
}

def _exit(msg):
    print(msg)
    print("Exiting in 5 seconds..")
    sleep(5)
    sys.exit(-1)

def pack(target_folder, output_ipk, config_data):
    # Collect file information
    file_info = []
    raw_data = b''
    offset = 0  # Initial offset value
    num_files = 0  # Initialize the count of files

    for root, _, files in os.walk(target_folder):
        for file_name in files:
            full_path = os.path.join(root, file_name)
            rel_path = os.path.relpath(root, target_folder)  # Relative path without filename
            file_size = os.path.getsize(full_path)
            last_modified = int(os.path.getmtime(full_path))

            # If getmtime returns 0, use getctime instead
            if last_modified == 0:
                last_modified = int(os.path.getctime(full_path))

            if not rel_path.endswith('/'):
                rel_path += '/'

            with open(full_path, 'rb') as file:
                readedFile = file.read()
                if any(file_name.endswith(substring) for substring in config_data.get('compress', default_config['compress'])):
                    if config_data.get('method', default_config['method']) == "lzma":
                        print(f"lzma: Compressing: {file_name}  ", end="\r")
                        file_data = lzma.compress(readedFile)
                    else: ## Newer IPK's uses LZMA for compression, old one uses zlib, theyre both working in new version
                        print(f"zlib: Compressing: {file_name}  ", end="\r")
                        file_data = zlib.compress(readedFile, level=zlib.Z_BEST_COMPRESSION)
                    origin_size = len(readedFile)
                    compressed_size = len(file_data)
                else:
                    file_data = readedFile
                    origin_size = len(readedFile)
                    compressed_size = 0
                raw_data += file_data

            # Calculate name and path sizes
            name_size = len(file_name.encode())
            path_size = len(rel_path.encode())

            file_info.append({
                'file_name': file_name.encode(),
                'path_name': rel_path.encode(),
                'file_size': origin_size,
                'compressed_size': compressed_size,
                'time_stamp': last_modified,
                'offset': offset,
                'name_size': name_size,
                'path_size': path_size,
                'checksum': zlib.crc32(full_path.encode())
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
            ipk_file.write(struct.pack(ENDIANNESS + STRUCT_SIGNS[4], 0))  # flag, set to 0

        # Write the raw data at the end of the file
        ipk_file.write(raw_data)

    print(f"\nLog: Packing completed to {output_ipk}.")

# Get the output IPK file name
default_config = {
    'jdversion': 2017,
    'compress': ['.dtape.ckd', '.fx.fxb', '.m3d.ckd', '.png.ckd', '.tga.ckd'],
    'method': 'zlib'
}

# Check if the config.json file exists
config_file_path = 'config.json'
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