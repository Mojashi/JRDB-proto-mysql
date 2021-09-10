from typing import Mapping


DocDir = "doc"
DataDir = "data"
ProtoDir = "proto"
ProtoBuildDir = ProtoDir + "/build"
DTypeListFlie = "typelist.json"
ProtoMySQLDir = "../proto-mysql"


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


# 下で設定するaliasをかける前の名前で指定
KnownFieldTypes = {
    r"他データリンク用キー\s.*": str,
    r"他データリンク用キー \s.*": str,
    r"競走馬該当条件別着度数集計\s.*": str,
    r"該当条件別着度数\s.*": str,
    r"着度数\s.*": str,
    "収得賞金": float,
    "本賞金": float,
    "一週前追切コース": str,
}

# 下で設定するaliasをかける前の名前で指定
KnownIgnoredFieldFullName = set([
    "走法",
])
KnownIgnoredFieldName = set([
    "改行",
    "予備",
])


# 親項目の名前を置き換え
KnownFieldParentNameAlias = {
    "競走馬該当条件別着度数集計": "statistics",
    "該当条件別着度数": "statistics",
}
