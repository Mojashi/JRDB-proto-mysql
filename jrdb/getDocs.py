#! python
import logging
from env import DTypeListFlie, DocDir

baseURL = "http://www.jrdb.com/program/%s/%s"

import requests
def get(dtypeName : str, docPath : str = None) -> bytes:
    url = baseURL % (
            dtypeName.capitalize(), 
            docPath if docPath != None and len(docPath) > 0 else
             dtypeName.lower() + "_doc.txt"
        )
    logging.info("GET %s" % url)
    resp = requests.get(url) 
    logging.info(resp.status_code)
    c = resp.content
    resp.close()
    return c

import os
import json
def getAll(docDir : str = DocDir ,listFile : str = DTypeListFlie):
    os.makedirs(docDir, exist_ok=True)

    with open(listFile, "r") as f:
        typeDescs = json.load(f)
    
    for typeDesc in typeDescs:
        dtname = typeDesc["name"]
        docpath = typeDesc.get("docfile")
        with open(docDir + "/" + dtname, "w") as docf:
            docf.write(get(dtname,docpath).decode("shift-jis"))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    getAll()