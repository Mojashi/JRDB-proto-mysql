#! python
import threading
from db.config import TableConfigs
from google.protobuf import json_format
from mysql.connector.cursor import CursorBase
import os
from setupDB import getConn
from utils import getDtypeDataDir
from model.schema import Convertor, DataType
from typing import IO, Any, List
from env import DataDir, DtypeDescs, ProtoBuildDir
from parseDoc import getDataType
import logging
import time
import glob
import sys
import queue
import itertools


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


def insertAllData(cur: CursorBase, dtypeName: str,
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
    columnList: List[str] = getattr(sqlModule, "get%sColumnNames" % dtypeName.capitalize())()

    conf = TableConfigs[dtypeName]
    ignore = "IGNORE" if conf.ignoreDuplicate else ""

    files = sorted(glob.glob(dir + "/%s*.txt" % dtypeName.upper()))

    que: queue.Queue = queue.Queue(100)

    def processQueue(que: queue.Queue, outputFile: str):
        with open(outputFile, "a") as f:
            while True:
                rows = que.get()
                # finish signal
                if len(rows) == 0:
                    return

                try:
                    for value in map(lambda row: insertConvFunc(row), rows):
                        for elem in value:
                            if type(elem) == bytes:
                                f.write(elem.hex())
                            elif elem is None:
                                f.write(r"\N")
                            else:
                                f.write(str(elem))
                            f.write("\t")
                        f.write("\n")
                except Exception as e:
                    with open("dump.log", "w") as f:
                        for r in rows:
                            f.write(json_format.MessageToJson(r))
                    raise e

    dataFileName = "/var/lib/mysql-files/loaddata.txt"

    if os.path.exists(dataFileName):
        os.remove(dataFileName)
    th = threading.Thread(target=processQueue,
                          args=(que, dataFileName), daemon=True)
    th.start()

    for fname in files:
        logging.info(fname)
        with open(fname, "rb", 100000) as f:
            que.put(parseData(ProtoT, dtype, fieldConvertors, f))

    que.put([])  # send finish signal
    th.join()

    logging.info("load data into DB")
    cur.execute('LOAD DATA INFILE "%s" %s '
                'INTO TABLE %s (%s) SET PROTO_BINARY=UNHEX(@proto_binary)' %
                (dataFileName, ignore, dtypeName.capitalize(),
                 ",".join(columnList[:-1] + ["@proto_binary"])))


def checkEmpty(cur: CursorBase, tableName: str) -> bool:
    cur.execute(f"SELECT 1 from {tableName} limit 1")
    for _ in cur:
        return False
    return True


def main():
    with getConn() as conn:
        conn.autocommit = False
        cur = conn.cursor()

        if len(sys.argv) > 1:
            if sys.argv[1].lower() not in DtypeDescs.keys():
                logging.error("unknown dtype")
                exit(1)
            insertAllData(cur, sys.argv[1])
            conn.commit()
        else:
            for dtypeName in DtypeDescs.keys():
                if not checkEmpty(cur, dtypeName.capitalize()):
                    continue
                insertAllData(cur, dtypeName)
                conn.commit()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
    # import cProfile
    # cProfile.run('main()', "prof")
    exit(0)
