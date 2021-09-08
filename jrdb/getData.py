#! python
from datetime import datetime
from requests.auth import HTTPBasicAuth
import requests
import os
import io
import time
import zipfile
import re
import logging
from typing import List, Tuple
from env import DataDir, DtypeDescs
from secret import JRDB_USER_ID, JRDB_PASSWORD
from utils import getDtypeDataDir


def splitZipName(name: str) -> Tuple[str, str]:
    # "CYB210815.zip" -> ("CYB", "210815")
    idx = next(i for i, v in enumerate(name) if v.isnumeric())
    return name[:idx], name[idx:-4]


def getFileName(scname: str, date: str) -> str:
    return scname.upper() + date + ".txt"


def getZipName(scname: str, date: str) -> str:
    return scname.upper() + date + ".zip"


def getYearPackDLURL(dtypeName: str, year: int) -> str:
    downloadBaseURL = "http://www.jrdb.com/member/datazip/%s/%s_%d.zip"
    return downloadBaseURL % (dtypeName.capitalize(), dtypeName.upper(), year)


def getSpecificDateDLURL(dtypeName: str, date: str) -> str:
    downloadBaseURL = "http://www.jrdb.com/member/datazip/%s/%d/%s"
    return downloadBaseURL \
        % (dtypeName.capitalize(), yearFromDate(date), getZipName(dtypeName, date))


prevDLTime = datetime.now()


def GETWithAuth(url: str):
    global prevDLTime
    if (datetime.now() - prevDLTime).total_seconds() < 0.1:
        time.sleep(0.1 - (datetime.now() - prevDLTime).total_seconds())

    logging.info("GET %s" % url)
    resp = requests.get(
        url,
        auth=HTTPBasicAuth(JRDB_USER_ID, JRDB_PASSWORD)
    )
    logging.info(resp.status_code)
    c = resp.content
    resp.close()
    prevDLTime = datetime.now()
    return c


def getListURL(dtypeName: str) -> str:
    listBaseURL = "http://www.jrdb.com/member/datazip/%s/index.html"
    return listBaseURL % dtypeName.capitalize()


def getList(dtypeName: str) -> List[str]:
    url = getListURL(dtypeName)
    body = re.findall(r"単体データコーナー.*</UL>",
                      GETWithAuth(url).decode("shift-jis"), re.MULTILINE | re.DOTALL)[0]
    return re.findall(r"href=\"\d+/(.+)\"", body)


def extractYearPack(dtypeName: str, year: int, dir: str):
    os.makedirs(dir, exist_ok=True)
    try:
        zipfile.ZipFile(io.BytesIO(
            GETWithAuth(getYearPackDLURL(dtypeName, year)))
        ).extractall(dir)
    except zipfile.BadZipFile:
        # 存在しなかったりしても許せる
        pass


def extractSpecificDate(dtypeName: str, date: str, dir: str):
    os.makedirs(getDtypeDataDir(dtypeName), exist_ok=True)
    zipfile.ZipFile(io.BytesIO(
        GETWithAuth(getSpecificDateDLURL(dtypeName, date)))
    ).extractall(dir)


def yearFromDate(date: str) -> int:
    if date[:2] == "99":
        return 1999
    else:
        return int("20" + date[:2])


def dlMissingFile(dtypeName: str, dataDir: str = DataDir):
    parentDtypeName = DtypeDescs[dtypeName.lower()].dataIncludedIn
    dir = getDtypeDataDir(parentDtypeName)
    files = getList(parentDtypeName)

    os.makedirs(dir, exist_ok=True)

    notFoundListFName = dataDir + "/notFoundList.txt"
    notFoundList = []
    if os.path.exists(notFoundListFName):
        with open(notFoundListFName, "r") as f:
            notFoundList = list(map(lambda line: line.strip(), f.readlines()))

    extractedYear = set()

    for name in files:
        date = splitZipName(name)[1]
        year = yearFromDate(date)
        fname = getFileName(dtypeName, date)
        logging.debug(fname)

        if fname in notFoundList:
            logging.info(fname + " was not found before")
            continue

        while not os.path.exists(dir + "/" + fname):
            # まれに、パックに入っていないことがある
            if year in extractedYear or year == datetime.now().year:
                extractSpecificDate(parentDtypeName, date, dir)
                break
            else:
                extractYearPack(parentDtypeName, year, dir)
                extractedYear.add(year)
        if not os.path.exists(dir + "/" + fname):
            with open(notFoundListFName, "a") as f:
                f.write(fname + "\n")
            logging.warning("failed to find data. %s" % fname)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for dtypeName in DtypeDescs.keys():
        dlMissingFile(dtypeName)
