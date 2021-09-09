#!python
# create table
# add primary index
# make generated column
from db.config import TableConfig, TableConfigs
from typing import List
import mysql.connector
from mysql.connector.cursor import CursorBase
import glob
import logging
from env import ProtoBuildDir
from secret import DB_USER, DB_HOST, DB_NAME, DB_PASS


def getConn():
    return mysql.connector.connect(
        user=DB_USER,
        host=DB_HOST,
        database=DB_NAME,
        password=DB_PASS)


def makeTable(cur: CursorBase):
    statements: List[str] = []
    for sqlFile in glob.glob(ProtoBuildDir + "/*.sql"):
        with open(sqlFile, "r") as f:
            statements.append(f.read())

    for stat in statements:
        cur.execute(stat)


def setup(cur: CursorBase, conf: TableConfig):
    for stat in conf.generatedColumns:
        cur.execute("ALTER TABLE %s ADD %s", conf.name, stat)
    cur.execute("ALTER TABLE %s ADD PRIMARY KEY (%s)", conf.name, ",".join(conf.primaryKey))
    for idxName, cols in conf.indexes:
        cur.execute("ALTER TABLE %s ADD INDEX %s(%s)", conf.name, idxName, ",".join(cols))


def removeTables(cur: CursorBase):
    pass    


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    conn = getConn()
    cur = conn.cursor()
    makeTable(cur)
    for conf in TableConfigs:
        setup(cur, conf)
