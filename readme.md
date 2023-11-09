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
- **Multiple IPK Type:** This tool supports both new and old .IPK

## Compatibility

Currently, Ubiart Archive Tools are compatible with the following games:

- Raymans Origins
- Raymans Legends
- Just Dance 2014
- Just Dance 2015-2022 (2017)
- Child Of Lights

Several other games can be configured manually,
to use one of the games above, use the preconfigured ones below

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
- InvoxiPlayGames

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Pre-configured Games
| Game name                 | Version | Game ID    | Engine Version | Switch Title |
|---------------------------|---------|------------|----------------|--------------|
| Rayman Origins (Demo)     | 3       | 2727956186 | 0              | true         |
| Rayman Legends (Demo)     | 5       | 1274838019 | 0              | true         |
| Just Dance 2014           | 5       | 472168730  | 0              | true         |
| Just Dance 2017 (PC)      | 5       | 490359856  | 253653         | false        |
| Child of Light (Demo)     | 7       | 3669482532 | 30765          | false        |

## Acknowledgments

- Special thanks to the contributors mentioned above for their valuable input and assistance.

Feel free to contribute to this project or report any issues you encounter. Happy modding!