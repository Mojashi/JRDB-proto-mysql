#! python
from utils import getDtypeDataDir
from model.schema import DataType, Field
from typing import IO, Union, Optional
from env import DataDir, ProtoBuildDir
from parseDoc import getDataType
import logging
import glob


def convType(field: Field, s: bytes) -> Union[Optional[int], Optional[float], str]:
    if field.pyType == str:
        return s.decode("cp932").strip()
    elif field.pyType == int:
        try:
            return int(s, 16 if "F" in field.docType else 10)
        except ValueError:
            if len(s.strip()) == 0:
                return None
            else:
                return int(float(s))
    elif field.pyType == float:
        try:
            return float(s)
        except ValueError:
            if len(s.strip()) == 0:
                return None
            else:
                return float(s)
    assert(True)
    return None


def parseData(ProtoT, dtype: DataType, data: IO):

    def parseRow():
        ret = ProtoT()
        for field in dtype.fields:
            # logging.debug(field.name)

            for _ in range(field.occ):
                s = data.read(field.size)
                if not s:
                    return None
                # logging.debug(s)

                if not field.ignored:
                    v = convType(field, s)
                    if v is None:
                        continue
                    if field.occ == 1:
                        setattr(ret, field.translatedName, v)
                    else:
                        getattr(getattr(ret, field.translatedName), "append")(v)
        return ret

    while True:
        row = parseRow()
        if row is None:
            break


def parseAllData(dtypeName: str, dataDir: str = DataDir, protoBuildDir: str = ProtoBuildDir):
    dir = getDtypeDataDir(dtypeName, dataDir)
    files = sorted(glob.glob(dir + "/*"))

    fromName = protoBuildDir.replace("/", ".")
    pbModule = __import__(fromName + ".%s_pb2" %
                          dtypeName, fromlist=[fromName])
    dtype = getDataType(dtypeName)
    ProtoT = getattr(pbModule, dtype.dtname.capitalize())

    for fname in files:
        print(fname)
        with open(fname, "rb", 100000) as f:
            parseData(ProtoT, dtype, f)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parseAllData("sed")
    # import cProfile
    # cProfile.run('parseAllData("sed")', "prof")
