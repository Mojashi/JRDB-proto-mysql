# create table
# add primary index
# make generated column
from typing import List, Mapping
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


raceKeyIndex = "idx_raceKey(racekey)"
raceKeyWithHorseNumIndex = "idx_raceKey(racekey, umaban)"


def createPrimaryKey(cur: CursorBase, primaryKeys: Mapping[str, str] = {
    "sed": "idx_"
}):
    cur.execute("SHOW TABLES")

    tables = []
    for (tableName,) in cur:
        tables.append(tableName)

    for table in tables:


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    conn = getConn()
    cur = conn.cursor()
    makeTable(cur)
    createPrimaryKey(cur)