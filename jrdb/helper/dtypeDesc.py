from typing import List, Mapping, Optional
from env import DTypeListFlie

class DtypeDesc:
    name : str
    dataIncludedIn : str
    docfile : str

    def __init__(self, name:str,dataIncludedIn:str = None,docfile:str = None) -> None:
        self.name = name
        self.dataIncludedIn = dataIncludedIn if dataIncludedIn != None else name
        self.docfile = docfile if docfile != None else name+ "_doc.txt"
        pass

import json
def readDtypeDescs(listFile : str = DTypeListFlie) -> Mapping[str, DtypeDesc]:
    ret = {}
    with open(listFile, "r") as f:
        typeDescs = json.load(f)
    for d in typeDescs:
        ret[d["name"]] = DtypeDesc(d["name"], d.get("dataIncludedIn"), d.get("docfile"))

    return ret