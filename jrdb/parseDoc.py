#! python
# https://scrapbox.io/exkeiba/doc%E3%81%AEparse

from typing import List
from env import DocDir, ProtoDir
from model.schema import DataType, Field
import logging
import functools

def getBody(lines: List[str])->List[str]:
    astindex = []
    lines = list(filter(lambda line: len(line.strip()) > 0, lines))
    for idx,line in enumerate(lines):
        # line = line.strip()
        logging.debug(line)
        if line.count("*") == len(line):
            astindex.append(idx)
    
    logging.debug(astindex)
    return lines[astindex[1] + 1:astindex[2]]

def parseDoc(doc: str, dtname:str) -> DataType:
    body = getBody(doc.split("\n"))
    dtype = DataType(dtname)

    parent = ""
    for line in body:
        terms = line.split()

        isChild = len(terms) > 0 and line[0].isspace()
        isParent = len(terms) == 1 and not line[0].isspace()
        haveOcc = len(terms) >= 5 and terms[1].isdigit() and terms[2].isdigit() and terms[4].isdigit()
        isRecord = len(terms) >= 4 and (
            haveOcc and terms[1].isdigit() and terms[2].isdigit() and terms[4].isdigit() or 
            not haveOcc and terms[1].isdigit() and terms[3].isdigit())

        logging.debug(line)
        logging.debug(terms)
        logging.debug([isRecord, isChild, isParent, haveOcc])

        if isRecord:
            if haveOcc:
                field = Field(terms[0], int(terms[1]), int(terms[2]), terms[3], int(terms[4]), terms[5] if len(terms) >= 6 else "")
            else:
                field = Field(terms[0], 1, int(terms[1]), terms[2], int(terms[3]), terms[4] if len(terms) >= 5 else "")
            if isChild:
                field.name = parent+'_'+field.name

            dtype.fields.append(field)

        if isParent:
            parent = terms[0]

    return dtype

def getDataType(dtname : str, docDir:str = DocDir) -> DataType:
    with open(docDir + "/" + dtname, "r") as f:
        return parseDoc(f.read(), dtname)

import os
def parseAll(docDir:str = DocDir, protoDir : str = ProtoDir):
    os.makedirs(protoDir, exist_ok=True)

    for docfname in os.listdir(docDir):
        dtype = getDataType(docfname)
        with open(protoDir + "/" + dtype.dtname + ".proto", "w") as protof:
            protof.write(dtype.genProto())


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    parseAll()