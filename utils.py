from posixpath import basename
from typing import IO, Any, Iterable, Tuple
from parseDoc import getDataType
from env import DataDir, DocDir


def getDtypeDataDir(dtypeName: str, dataDir: str = DataDir):
    return dataDir + "/" + dtypeName.lower()


def isEveryHorseInfo(dtypeName: str, docDir: str = DocDir):
    return "馬番" in \
        map(lambda f: f.originalFullName, getDataType(dtypeName, docDir).fields)


def splitZipName(name: str) -> Tuple[str, str]:
    # "CYB210815.zip" -> ("CYB", "210815")
    idx = next(i for i, v in enumerate(name) if v.isnumeric())
    return name[:idx], name[idx:-4]


def splitTxtName(name: str) -> Tuple[str, str]:
    # "CYB210815.txt" -> ("CYB", "210815")
    idx = next(i for i, v in enumerate(name) if v.isnumeric())
    return name[:idx], name[idx:-4]


def getDateFromL2Date(date: str) -> str:
    # "991012" -> "19991012"
    return ("19"+date) if date[:2] == "99" else ("20" + date)


def getFileName(scname: str, date: str) -> str:
    return scname.upper() + date + ".txt"


def getZipName(scname: str, date: str) -> str:
    return scname.upper() + date + ".zip"


def yearFromDate(date: str) -> int:
    if date[:2] == "99":
        return 1999
    else:
        return int("20" + date[:2])


def writeMutipleProto(protos: Iterable[Any], f: IO[bytes]):
    for r in protos:
        d = r.SerializeToString()
        f.write(len(d).to_bytes(length=4, byteorder="little"))
        f.write(d)
