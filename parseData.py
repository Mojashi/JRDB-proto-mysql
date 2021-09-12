#! python
import threading
from db.config import TableConfigs
from google.protobuf import json_format
from mysql.connector.cursor import CursorBase
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
    columnList = getattr(sqlModule, "get%sColumnNames" % dtypeName.capitalize())()

    conf = TableConfigs[dtypeName]
    ignore = "IGNORE" if conf.ignoreDuplicate else ""

    files = sorted(glob.glob(dir + "/%s*.txt" % dtypeName.upper()))

    que: queue.Queue = queue.Queue(-1)

    def processQueue(que: queue.Queue, outputFile: str):
        while True:
            time.sleep(0.1)
            cr: List[List[Any]] = []
            try:
                while True:
                    cr.append(que.get_nowait())
            except queue.Empty:
                pass
            if len(cr) == 0:
                continue
            logging.info(len(cr))
            rows = itertools.chain.from_iterable(cr)
            try:
                values = list(map(lambda row: insertConvFunc(row), rows))
                # holders = ",".join([r"%s" for _ in range(len(values[0]))])
                # logging.info("a")
                # cur.executemany(f"INSERT {ignore} INTO {dtypeName.capitalize()} "
                #                 f"({columnList}) VALUES ({holders})", values)
                with open(outputFile, "a") as f:
                    for value in values:
                        for elem in value:
                            if type(elem) == bytes:
                                f.write(elem.hex())
                            elif elem is None:
                                f.write(r"\N")
                            else:
                                f.write(str(elem))
                            f.write("\t")
                        f.write("\n")
                logging.info("b")
            except Exception as e:
                with open("dump.log", "w") as f:
                    for r in rows:
                        f.write(json_format.MessageToJson(r))
                raise e

    th = threading.Thread(target=processQueue,
        args=(que, "/var/lib/mysql-files/loaddata.txt"), daemon=True)
    th.start()

    for fname in files:
        logging.info(fname)
        with open(fname, "rb", 100000) as f:
            que.put(parseData(ProtoT, dtype, fieldConvertors, f))

    cur.execute('LOAD DATA INFILE "/var/lib/mysql-files/loaddata.txt" %s'
                'into table Cyb (%s) SET PROTO_BINARY=UNHEX(@var1);' % (ignore, columnList))


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
    import cProfile
    cProfile.run('main()', "prof")
    exit(0)
