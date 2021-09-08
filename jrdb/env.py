from typing import Mapping


DocDir = "doc"
DataDir = "data"
ProtoDir = "proto"
ProtoBuildDir = ProtoDir + "/build"
DTypeListFlie = "typelist.json"


class DtypeDesc:
    name: str
    dataIncludedIn: str
    docfile: str

    def __init__(self, name: str, dataIncludedIn: str = None, docfile: str = None) -> None:
        self.name = name
        self.dataIncludedIn = dataIncludedIn if dataIncludedIn is not None else name
        self.docfile = docfile if docfile is not None else name + "_doc.txt"
        pass


DtypeDescs: Mapping[str, DtypeDesc] = {
    "sed": DtypeDesc("sed"),
    "srb": DtypeDesc("srb", dataIncludedIn="sed"),
    "kyi": DtypeDesc("kyi"),
    "kka": DtypeDesc("kka"),
    "ukc": DtypeDesc("ukc"),
    "oz": DtypeDesc("oz", docfile="Ozdata_doc.txt"),
    "bac": DtypeDesc("bac"),
    "cyb": DtypeDesc("cyb"),
    "cha": DtypeDesc("cha"),
    "tyb": DtypeDesc("tyb"),
}


KnownFieldTypes = {
    "他データリンク用キー 前走１競走成績キー": str,
    "他データリンク用キー 前走２競走成績キー": str,
    "他データリンク用キー 前走３競走成績キー": str,
    "他データリンク用キー 前走４競走成績キー": str,
    "他データリンク用キー 前走５競走成績キー": str,
    "他データリンク用キー 前走１レースキー": str,
    "他データリンク用キー 前走２レースキー": str,
    "他データリンク用キー 前走３レースキー": str,
    "他データリンク用キー 前走４レースキー": str,
    "他データリンク用キー 前走５レースキー": str,
}

KnownIgnoredFields = set([
    "走法"
])
