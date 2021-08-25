#! python
# https://scrapbox.io/exkeiba/doc%E3%81%AEparse

from typing import List
from env import DocDir, ProtoDir
from model.schema import DataType
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
    assert(len(astindex) == 3)
    return lines[astindex[1] + 1:astindex[2]]

def parseDoc(doc: str) -> DataType:
    body = getBody(doc.split("\n"))
    logging.debug(body)
    
    return DataType()


import os
def parseAll(docDir:str = DocDir, protoDir : str = ProtoDir):
    os.makedirs(protoDir, exist_ok=True)

    for docfname in os.listdir(docDir):
        with open(docDir + "/" + docfname, "r") as f:
            dtype = parseDoc(f.read())
            with open(protoDir + "/" + dtype.dtname, "w") as protof:
                protof.write(dtype.genProto())


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    parseAll()