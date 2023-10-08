#
# https://github.com/PartyService/Ubiart-Archive-Tools
#
# UbiArt Archive Tools (IPK) is an useful scripts to extract or pack an .ipk
# 
# This Script Made Possible by Party Team, just gemer, Planedec50, leamsii, XpoZed
#

import os
import sys
import struct
from pathlib import Path
from time import sleep
import zlib
import lzma

# Define endianness as big endian
ENDIANNESS = '>'

# Define structure signs for various sizes
STRUCT_SIGNS = {
    1: 'c',
    2: 'H',
    4: 'I',
    8: 'Q'
}

# Define the structure of the IPK file header
IPK_HEADER = {
    'magic': {'size': 4},
    'version': {'size': 4},
    'platformsupported': {'size': 4},
    'base_offset': {'size': 4},
    'num_files': {'size': 4},
    'compressed': {'size': 4},  # Set to 0
    'binaryscene': {'size': 4},  # Set to 0
    'binarylogic': {'size': 4},  # Bundlelogic maybe??
    'datasignature': {'size': 4},
    'enginesignature': {'size': 4},  # Let's just say this is Just Dance 2017
    'engineversion': {'size': 4},  # This is the engine version used by JD17
    'num_files2': {'size': 4},
}


def _exit(msg):
    print(msg)
    print("Exiting in 5 seconds..")
    sleep(5)
    sys.exit(-1)


# Define the structure of chunks in the IPK files
def get_file_header():
    return {
        'numOffset': {'size': 4},
        'size': {'size': 4},
        'compressed_size': {'size': 4},
        'time_stamp': {'size': 8},
        'offset': {'size': 8},
        'name_size': {'size': 4},
        'file_name': {'size': 0},
        'path_size': {'size': 4},
        'path_name': {'size': 4},
        'checksum': {'size': 4},
        'flag': {'size': 4}
    }


def unpack(_bytes):
    return struct.unpack(ENDIANNESS + STRUCT_SIGNS[len(_bytes)], _bytes)[0]


# This function will handle the data extraction from the files
def extract(target_file):
    with open(target_file, 'rb') as file:
        # Get file header information
        for k, v in enumerate(IPK_HEADER):
            IPK_HEADER[v]['value'] = file.read(IPK_HEADER[v]['size'])

        # Check if this is a proper IPK file
        assert IPK_HEADER['magic']['value'] == b'\x50\xEC\x12\xBA'

        num_files = unpack(IPK_HEADER['num_files']['value'])
        print(f"Log: Found {num_files} files..")

        # Go through the file and collect the data
        file_chunks = []
        for _ in range(num_files):
            fHeader = get_file_header()
            for k, v in enumerate(fHeader):
                _size = fHeader[v]['size']

                if v == 'path_name':
                    _size = unpack(fHeader['path_size']['value'])
                if v == 'file_name':
                    _size = unpack(fHeader['name_size']['value'])

                fHeader[v]['value'] = file.read(_size)

            file_chunks.append(fHeader)

        # Create the directory for the extracted folders
        outputDir = Path(target_file.stem)
        outputDir.mkdir(exist_ok=True)
        os.chdir(outputDir)

        print(f"Log: Extracting data to {outputDir.name} in {Path.cwd()}..")
        base_offset = unpack(IPK_HEADER['base_offset']['value'])

        for k, v in enumerate(file_chunks):

            # File raw data
            offset = unpack(file_chunks[k]['offset']['value'])
            data_size = unpack(file_chunks[k]['size']['value'])

            # File names and creation
            path_ori = file_chunks[k]['path_name']['value'].decode()
            if os.path.basename(path_ori) == path_ori:
			  # Handling ipk v3, this applies to Just Dance 2014, Raymans Origins, Etc
              file_path = Path.cwd() / file_chunks[k]['file_name']['value'].decode() #utf8
              file_name =  file_chunks[k]['path_name']['value'].decode() 
            else:
			  # Handling ipk v4?? v5+, this applies to Just Dance 2015-2022, Child Of Lights, Etc
              print(f"A: {path_ori}")
              file_path = Path.cwd() / file_chunks[k]['path_name']['value'].decode() #utf8
              file_name = file_chunks[k]['file_name']['value'].decode()

            file.seek(offset + base_offset)

            # Make the sub directories
            file_path.mkdir(parents=True, exist_ok=True)

            # Inside the loop where you extract files
            with open(file_path / file_name, 'wb') as ff:
                readedFile = file.read(data_size)  # Check the magic bytes or unique identifier at the beginning of the file
                magic_bytes = readedFile[:4]  # Adjust this based on the expected identifier size

                try:
                    # Try to decompress with zlib
                    decompressed_data = zlib.decompress(readedFile)
                    print(f"zlib: decompressing {file_name}    ", end="\r")
                except zlib.error:
                    try:
                        # Try to decompress with lzma
                        decompressed_data = lzma.decompress(readedFile)
                        print(f"lzma: decompressing {file_name}    ", end="\r")
                    except:
                        # If neither zlib nor lzma decompression works, use the original data
                        decompressed_data = readedFile

                ff.write(decompressed_data)

    _exit("Log: Program finished.")


# Check if the proper arguments were given
args = sys.argv
if len(args) <= 1:
    _exit("Error: Please specify a target .IPK file to unpack! ie, ipk_unpack.py ipk_file")

# Check if the file exists
target_file = Path(args[1])
if not target_file.exists():
    _exit(f"Error: The file '{target_file.name}' was not found!")

# Unpack the file otherwise
extract(target_file)
