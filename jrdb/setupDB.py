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
from env import DtypeDescs, ProtoBuildDir
from secret import DB_USER, DB_HOST, DB_NAME, DB_PASS, UNIXSOCKET
import sys


def getConn():
    if UNIXSOCKET == "":
        return mysql.connector.connect(
            user=DB_USER,
            host=DB_HOST,
            database=DB_NAME,
            password=DB_PASS,
            charset='utf8')
    else:
        return mysql.connector.connect(
            user=DB_USER,
            unix_socket=UNIXSOCKET,
            database=DB_NAME,
            password=DB_PASS,
            charset='utf8')


def makeTable(cur: CursorBase, dtypeName: str):
    with open(ProtoBuildDir + f"/{dtypeName.lower()}.proto.sql", "r") as f:
        stat = f.read()
        logging.debug(stat)
        cur.execute(stat)


def setup(cur: CursorBase, conf: TableConfig):
    logging.info("setup " + conf.name)
    for stat in conf.generatedColumns:
        logging.debug("generatedColumn " + stat)
        cur.execute(f"ALTER TABLE {conf.name} ADD {stat}")
    stat = ",".join(conf.primaryKey)
    cur.execute(f"ALTER TABLE {conf.name} ADD PRIMARY KEY ({stat})")
    for idxName, cols in conf.indexes:
        stat = ",".join(cols)
        logging.debug("addIndex " + idxName)
        cur.execute(f"ALTER TABLE {conf.name} ADD INDEX {idxName}({stat})")


def removeTable(cur: CursorBase, table: str):
    logging.info("remove " + table)
    cur.execute("DROP TABLE %s" % table)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    with getConn() as conn:
        cur = conn.cursor()

        if len(sys.argv) > 1:
            removeTable(cur, sys.argv[1].capitalize())
            if sys.argv[1].lower() not in DtypeDescs.keys():
                logging.error("unknown dtype")
                exit(1)
            makeTable(cur, sys.argv[1])
            setup(cur, TableConfigs[sys.argv[1]])
        else:
            for dtypeName in DtypeDescs.keys():
                removeTable(cur, dtypeName.capitalize())
                makeTable(cur, dtypeName)
                setup(cur, TableConfigs[dtypeName])
