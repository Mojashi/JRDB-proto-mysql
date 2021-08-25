# JRDB parser

1. fetch JRDB docs and data.
2. generate .proto files for each JRDB-doc.
3. ~~convert JRDB data into protobuf format.~~  UPCOMING!

## Requirements
- python3
- google-protobuf
- xjrdb-account

## Use
```sh=
./getDocs.py  # fetch JRDB-docs 
./parseDoc.py # gen .proto files
```