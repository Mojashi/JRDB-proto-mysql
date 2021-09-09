#! python
from mysql.connector.cursor import CursorBase
from setupDB import getConn
from utils import getDtypeDataDir
from model.schema import Convertor, DataType
from typing import IO, Any, List
from env import DataDir, DtypeDescs, ProtoBuildDir
from parseDoc import getDataType
import logging
import glob


def parseData(ProtoT, dtype: DataType,
              fieldConvertors: List[Convertor], data: IO) -> List[Any]:

    def parseRow():
        ret = ProtoT()
        for field, convType in zip(dtype.fields, fieldConvertors):
            try:
                # logging.debug(field.name)

                for _ in range(field.occ):
                    s = data.read(field.size)
                    if field.originalName == "改行" and s != b"\r\n":
                        raise Exception("invalid format!!!")

                    if not s:
                        return None
                    # logging.debug(s)

                    if not field.ignored:
                        v = convType(s)
                        if field.occ == 1:
                            if v is None:
                                continue
                            setattr(ret, field.translatedName, v)
                        else:
                            getattr(getattr(ret, field.translatedName), "append")(
                                v if v is not None else 0)
            except Exception as e:
                raise Exception(field.originalFullName) from e
        return ret

    rows = []
    while True:
        row = parseRow()
        if row is None:
            break
        rows.append(row)

    return rows


def parseAllData(cur: CursorBase, dtypeName: str,
                 dataDir: str = DataDir, protoBuildDir: str = ProtoBuildDir):
    parentDtypeName = DtypeDescs[dtypeName.lower()].dataIncludedIn
    dir = getDtypeDataDir(parentDtypeName, dataDir)
    files = sorted(glob.glob(dir + "/%s*" % dtypeName.upper()))

    fromName = protoBuildDir.replace("/", ".")
    pbModule = __import__(fromName + ".%s_pb2" %
                          dtypeName, fromlist=[fromName])
    dtype = getDataType(dtypeName)
    fieldConvertors = dtype.fieldConvertors()
    ProtoT = getattr(pbModule, dtype.dtname.capitalize())

    sqlModule = __import__(fromName + ".%s_sqlhelper" %
                           dtypeName, fromlist=[fromName])
    insertConvFunc = getattr(sqlModule, "conv%sProtoClassToData" % dtypeName.capitalize())
    columnList = getattr(sqlModule, "get%sColumnNames" % dtypeName.capitalize())()

    rows = []
    for fname in files:
        print(fname)
        with open(fname, "rb", 100000) as f:
            rows.extend(parseData(ProtoT, dtype, fieldConvertors, f))

        # print(len(values[0]), values[0])

        if len(rows) > 1000:
            values = list(map(lambda row: insertConvFunc(row), rows))
            holders = ",".join([r"%s" for _ in range(len(values[0]))])
            cur.executemany(f"INSERT INTO {dtypeName.capitalize()} "
                            f"({columnList}) VALUES ({holders})", values)
            del rows
            rows = []

    cur.commit()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # for dtypeName in DtypeDescs.keys():
    #     parseAllData(dtypeName)
    conn = getConn()
    cur = conn.cursor()
    parseAllData(cur, "kyi")
    # import cProfile
    # cProfile.run('parseAllData("sed")', "prof")
