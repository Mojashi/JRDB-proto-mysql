#! python
# https://scrapbox.io/exkeiba/doc%E3%81%AEparse

import subprocess
import os
from typing import List
from env import DocDir, ProtoBuildDir, ProtoDir
from model.schema import DataType, Field
import logging


def getBody(lines: List[str]) -> List[str]:
    astindex = []
    lines = list(filter(lambda line: len(line.strip()) > 0, lines))
    for idx, line in enumerate(lines):
        # line = line.strip()
        logging.debug(line)
        if line.count("*") == len(line):
            astindex.append(idx)

    logging.debug(astindex)
    return lines[astindex[1] + 1:astindex[2]]


def parseDoc(doc: str, dtname: str) -> DataType:
    body = getBody(doc.split("\n"))
    dtype = DataType(dtname)

    parent = ""
    for line in body:
        terms = line.split()

        isChild = len(terms) > 0 and line[0].isspace()
        isParent = not line[0].isspace()
        haveOcc = len(terms) >= 5 and terms[1].isdigit() and\
            terms[2].isdigit() and terms[4].isdigit()
        isRecord = len(terms) >= 4 and (
            haveOcc and terms[1].isdigit() and terms[2].isdigit() and terms[4].isdigit() or
            not haveOcc and terms[1].isdigit() and terms[3].isdigit())

        logging.debug(line)
        logging.debug(terms)
        logging.debug([isRecord, isChild, isParent, haveOcc])

        if isRecord:
            name = terms[0]

            if haveOcc:
                field = Field(
                    name=name,
                    occ=int(terms[1]),
                    size=int(terms[2]),
                    docType=terms[3],
                    pos=int(terms[4]),
                    parentName=parent,
                    comment=terms[5] if len(terms) >= 6 else "")
            else:
                field = Field(
                    name=name,
                    occ=1,
                    size=int(terms[1]),
                    docType=terms[2],
                    pos=int(terms[3]),
                    parentName=parent,
                    comment=terms[4] if len(terms) >= 5 else "")

            dtype.fields.append(field)

            if not isChild:
                parent = ""

        if isParent:
            parent = terms[0]

    return dtype


def getDataType(dtname: str, docDir: str = DocDir) -> DataType:
    logging.info("parse "+dtname)
    with open(docDir + "/" + dtname, "r") as f:
        return parseDoc(f.read(), dtname)


def parseAll(docDir: str = DocDir, protoDir: str = ProtoDir):
    os.makedirs(protoDir, exist_ok=True)

    for docfname in os.listdir(docDir):
        dtype = getDataType(docfname)
        with open(protoDir + "/" + dtype.dtname + ".proto", "w") as protof:
            protof.write(dtype.genProto())


def execProtoc(protoDir: str = ProtoDir, protoBuildDir: str = ProtoBuildDir):
    logging.info("compile .proto")
    os.makedirs(protoBuildDir, exist_ok=True)
    subprocess.run("protoc --plugin=../proto-mysql/protoc-gen-mysql"
                   " --mysql_out=%s --python_out=%s -I%s %s/*.proto" %
                   (protoBuildDir, protoBuildDir, protoDir, protoDir), shell=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parseAll()
    execProtoc()
