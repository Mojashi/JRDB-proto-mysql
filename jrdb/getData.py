#! python
import logging
from typing import List
from env import DataDir
from bs4 import BeautifulSoup
from secret import JRDB_USER_ID,JRDB_PASSWORD

downloadBaseURL = "http://www.jrdb.com/member/datazip/%s/%s_%d.zip"
listBaseURL = "http://www.jrdb.com/member/datazip/%s/index.html"

def getYearPackDLURL(dtypeName : str, year : int) -> str:
    return downloadBaseURL % (dtypeName.capitalize(),dtypeName.upper(),year)
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
    logging.info(resp.status_code)
    c = resp.content
    resp.close()
    return c

from datetime import datetime
import zipfile
import io
import os
def extractYearPacks(dtypeName : str, dataDir:str = DataDir):
    os.makedirs(dataDir, exist_ok=True)
    for year in range(1999,datetime.now().year):
        z = zipfile.ZipFile(io.BytesIO(getYearPack(dtypeName,year)))
        z.extractall(dataDir)

def getMissingFile(dtypeName : str, dataDir:str = DataDir):
    os.makedirs(dataDir, exist_ok=True)
    files = getList(dtypeName)
    

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    extractYearPacks("sed")