#! python
from google.protobuf import json_format
from mysql.connector.cursor import CursorBase
from setupDB import getConn
from utils import getDtypeDataDir
from model.schema import Convertor, DataType
from typing import IO, Any, List
from env import DataDir, DtypeDescs, ProtoBuildDir
from parseDoc import getDataType
import logging
import glob
import sys


def parseData(ProtoT, dtype: DataType,
              fieldConvertors: List[Convertor], data: IO) -> List[Any]:

    def parseRow():
        ret = ProtoT()
        for field, convType in zip(dtype.fields, fieldConvertors):
            try:
                for _ in range(field.occ):
                    s = data.read(field.size)
                    if field.originalName == "改行" and s != b"\r\n":
                        raise Exception("invalid format!!!")
                    if not s:
                        return None
                
                    if not field.ignored:
                        try:
                            v = convType(s)
                        except Exception as e:
                            logging.error(e.args)
                            logging.error("field: " + field.originalFullName)
                            v = None

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
    files = sorted(glob.glob(dir + "/%s*.txt" % dtypeName.upper()))
    for fname in files:
        logging.info(fname)
        with open(fname, "rb", 100000) as f:
            rows.extend(parseData(ProtoT, dtype, fieldConvertors, f))

        # print(len(values[0]), values[0])

        if len(rows) > 10000:
            try:
                values = list(map(lambda row: insertConvFunc(row), rows))
                holders = ",".join([r"%s" for _ in range(len(values[0]))])
                cur.executemany(f"INSERT INTO {dtypeName.capitalize()} "
                                f"({columnList}) VALUES ({holders})", values)
                del rows
                rows = []
            except Exception as e:
                with open("dump.log", "w") as f:
                    for r in rows:
                        f.write(json_format.MessageToJson(r))
                raise e


def checkEmpty(cur: CursorBase, tableName: str) -> bool:
    cur.execute(f"SELECT 1 from {tableName} limit 1")
    for _ in cur:
        return False
    return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    conn = getConn()
    cur = conn.cursor()
    conn.autocommit = False

    if len(sys.argv) > 1:
        if sys.argv[1].lower() not in DtypeDescs.keys():
            logging.error("unknown dtype")
            exit(1)
        parseAllData(cur, sys.argv[1])
        conn.commit()
    else:
        for dtypeName in DtypeDescs.keys():
            if not checkEmpty(cur, dtypeName.capitalize()):
                continue
            parseAllData(cur, dtypeName)
            conn.commit()
    # parseAllData(cur, "srb")
    # import cProfile
    # cProfile.run('parseAllData("sed")', "prof")
