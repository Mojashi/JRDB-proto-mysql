from typing import Mapping


DtypeID = str


class DtypeDesc:
    name: DtypeID
    dataIncludedIn: str
    docfile: str

    def __init__(self, name: DtypeID, dataIncludedIn: str = None, docfile: str = None) -> None:
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
    "芝適性コード": int,
    "ダ適性コード": int,
    "ブリンカー":int,
    "見習い区分":int,
    "印コード 激走印":int,
    "展開予想データ ゴール内外": int,
    "取消フラグ":int,
    "性別コード":int,
    "降級フラグ":int,
    "輸送区分":int,
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

NonRaceInfoDtypes = set(["ukc"])
RaceInfoDtypes = set(DtypeDescs.keys()) - NonRaceInfoDtypes
