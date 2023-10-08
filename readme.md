# Ubiart Archive Tools

## Overview

Ubiart Archive Tools is a Python-based utility that allow us to creating and extracting Ubiart archives (.IPK). This tool offers a user-friendly for automodder, cli user.

## UbiArt Archive Format

UbiArt games use IPK files to store all related game files.
This format is a custom archive file where multiple files can be packed


## Features

- **Unpack (Extract):** Easily extract content from Ubiart archives.
- **Pack (Create):** Create Ubiart archives with ease.
- **Compression Support:** Compress files within the archives using zlib and LZMA.

## Compatibility

Currently, Ubiart Archive Tools are compatible with the following games:

- Just Dance 2015-2022

Compatibility for Just Dance 2014, Rayman Origins, and another ubiart games will be added in future updates.

## Usage

To use Ubiart Archive Tools, follow these commands:

- To pack (create) an IPK archive:
  ```
  python ipk_packer.py input_dir/ output.ipk
  ```

- To unpack (extract) an IPK archive:
  ```
  python ipk_unpacker.py input.ipk
  ```
- To use zlib or lzma, you can modify config.json
  ```
  "method": "lzma"
  ```

## Contributors

This project wouldn't be possible without the contributions of the following individuals:

- Party Team
- XpoZed (unpakke)
- planedec50
- leamsii

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgments

- Special thanks to the contributors mentioned above for their valuable input and assistance.

Feel free to contribute to this project or report any issues you encounter. Happy archiving!