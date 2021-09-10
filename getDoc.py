#! python
import os
import requests
import logging
from env import DocDir, DtypeDescs

baseURL = "http://www.jrdb.com/program/%s/%s"


def get(dtypeName: str, docPath: str = None) -> bytes:
    url = baseURL % (
        dtypeName.capitalize(),
        docPath if docPath is not None and len(docPath) > 0 else
        dtypeName.lower() + "_doc.txt"
    )
    logging.info("GET %s" % url)
    resp = requests.get(url)
    logging.info(resp.status_code)
    c = resp.content
    resp.close()
    return c


def getAll(docDir: str = DocDir):
    os.makedirs(docDir, exist_ok=True)

    for dtname, typeDesc in DtypeDescs.items():
        docpath = typeDesc.docfile
        with open(docDir + "/" + dtname, "w") as docf:
            docf.write(get(dtname, docpath).decode("shift-jis"))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    getAll()
