#! python
import logging
from typing import List
from env import DTypeListFlie, DocDir
from bs4 import BeautifulSoup
from secret import JRDB_USER_ID,JRDB_PASSWORD

downloadBaseURL = "http://www.jrdb.com/member/datazip/%s/%s_%d.zip"
listBaseURL = "http://www.jrdb.com/member/datazip/%s/index.html"

def getYearPackDLURL(dtypeName : str, year : int) -> str:
    return downloadBaseURL % (dtypeName.capitalize(),dtypeName.capitalize(),year)
def getListURL(dtypeName : str) -> str:
    return listBaseURL % dtypeName.capitalize()

import requests
import re
from requests.auth import HTTPBasicAuth 
def getList(dtypeName : str) -> List[str]:
    url = getListURL(dtypeName)
    logging.info("GET %s" % url)
    resp = requests.get(
        url,
        auth=HTTPBasicAuth(JRDB_USER_ID, JRDB_PASSWORD)
    ) 
    c = resp.content.decode("shift-jis")
    resp.close()
    soup = BeautifulSoup(c, "lxml")
    return re.findall("href=\"(.+)\"",str(list(soup.find_all("ul"))[1]))

def getYearPack(dtypeName : str, year : int) -> bytes:
    url = getYearPackDLURL(dtypeName, year)
    logging.info("GET %s" % url)
    resp = requests.get(
        url,
        auth=HTTPBasicAuth(JRDB_USER_ID, JRDB_PASSWORD)
    ) 
    c = resp.content
    resp.close()
    return c

def getYearPacks(dtypeName : str) -> bytes:
    url = getYearPackDLURL(dtypeName, year)
    logging.info("GET %s" % url)
    resp = requests.get(
        url,
        auth=HTTPBasicAuth(JRDB_USER_ID, JRDB_PASSWORD)
    ) 
    c = resp.content
    resp.close()
    return c


import os
def getAll(docDir : str = DocDir ,listFile : str = DTypeListFlie):
    os.makedirs(docDir, exist_ok=True)

    with open(listFile, "r") as f:
        for dtname in f.readlines():
            dtname, docpath = dtname.strip().split(",")
            with open(docDir + "/" + dtname, "w") as docf:
                docf.write(get(dtname,docpath).decode("shift-jis"))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(getList("sed"))