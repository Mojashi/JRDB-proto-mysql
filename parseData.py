#! python
from sys import argv
from parseData import parseIndivisual, parseRaceInfo
from config import NonRaceInfoDtypes
from env import ParsedDataDir
from os import makedirs
import logging
import sys


sys.path.append('../')


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    makedirs(ParsedDataDir, exist_ok=True)

    if len(argv) > 1:
        dtname = argv[1]
        parseIndivisual(ParsedDataDir + f"/{dtname.lower()}.dat", dtname)
    else:
        parseRaceInfo(ParsedDataDir + "/raceinfo.dat")
        for dtname in NonRaceInfoDtypes:
            parseIndivisual(ParsedDataDir + f"/{dtname.lower()}.dat", dtname)
