from model.conv import convFloatType, convIntTypeDEC, convIntTypeHEX, convSignedFloatType
from model.conv import convSignedIntTypeDEC, convSignedIntTypeHEX, convStrType
import pykakasi
from typing import Callable, Dict, List, Optional, Type, Union
from env import KnownFieldParentNameAlias, KnownIgnoredFieldFullName,\
     KnownIgnoredFieldName, KnownFieldTypes
import re


Convertor = Callable[[bytes], Optional[Union[int, float, str]]]
MAX_FIELD_NAME_LENGTH = 64


class Field:
    originalParentName: str
    originalName: str
    originalFullName: str
    fullName: str
    translatedName: str

    occ: int
    size: int
    docType: str
    pyType: Type
    pos: int
    comment: str
    ignored: bool

    def __init__(self, name: str, occ: int, size: int, docType: str, pos: int,
                 parentName: str = "", comment: str = "", ignored=False) -> None:
        self.originalName = name
        self.originalParentName = parentName

        if parentName != "":
            palias = KnownFieldParentNameAlias.get(parentName, parentName)
            self.fullName = palias + " " + name
            self.originalFullName = parentName + " " + name
        else:
            self.fullName = name
            self.originalFullName = name

        self.size = size
        self.occ = occ
        self.docType = docType
        self.pos = pos
        self.comment = self.originalParentName + ">" + self.originalName + " " + comment

        if self.occ > 1:
            self.comment += " repeated:%dtimes" % self.occ

        self.ignored = ignored or\
            self.originalFullName in KnownIgnoredFieldFullName or\
            self.originalName in KnownIgnoredFieldName

        self.translatedName = translate(self.fullName)
        if len(self.translatedName) > MAX_FIELD_NAME_LENGTH:
            raise Exception("field name is too long!")

        if name in KnownFieldTypes:
            self.pyType = KnownFieldTypes[name]
        elif docType[0] == 'X':
            # 最初のXは符号っぽい
            if re.fullmatch(r"X[Z9]+", docType):
                self.pyType = int
            elif re.fullmatch(r"X[Z9]+\.9+", docType):
                self.pyType = float
            else:
                self.pyType = str
        elif "." in docType:
            self.pyType = float
        else:
            self.pyType = int

    def genProtoField(self, num: int) -> str:
        return "\t{repeated} {type} {name} = {num}; {comment}".format(
            repeated="repeated" if self.occ > 1 else "optional",
            type="string" if self.pyType == str else (
                ("int32" if self.size <=
                 9 else "int64") if self.pyType == int else "float"
            ),
            name=self.translatedName,
            num=num,
            comment="" if self.comment == "" else "//"+self.comment)

    def getIgnored(self) -> bool:
        return self.ignored

    def getOcc(self) -> int:
        return self.occ

    def getConvFunc(self) -> Convertor:
        if self.pyType == str:
            return convStrType
        else:
            if self.docType[0] == "X":
                if self.pyType == int:
                    if "F" in self.docType:
                        return convSignedIntTypeHEX
                    else:
                        return convSignedIntTypeDEC
                if self.pyType == float:
                    return convSignedFloatType
            if self.pyType == int:
                if "F" in self.docType:
                    return convIntTypeHEX
                else:
                    return convIntTypeDEC
            if self.pyType == float:
                return convFloatType
            assert(True)
            return convStrType


class DataType:
    dtname: str
    fields: List[Field]

    def __init__(self, dtname: str) -> None:
        self.dtname = dtname
        self.fields = []

    def genProto(self) -> str:
        fields = "\n".join(map(lambda ifield: ifield[1].genProtoField(
            ifield[0] + 1), enumerate(filter(lambda f: not f.getIgnored(), self.fields))))
        return 'syntax = "proto3";\nmessage %s {\n%s\n}' % (self.dtname.capitalize(), fields)

    def fieldConvertors(self) -> List[Convertor]:
        return list(map(lambda field: field.getConvFunc(), self.fields))


kks = pykakasi.kakasi()


prechar = {'(': 'かっこ', ')': 'かっこ'}


def translate(jp: str, endict: Dict[str, str] = {
    '1': 'one', '2': 'two', '3': 'three', '4': 'four', '5': 'five', '6': 'sic', '7': 'seven',
    '8': 'eight', '9': 'nine', '0': 'zero', '10': 'ten',
    '１': 'one', '２': 'two', '３': 'three', '４': 'four', '５': 'five', '６': 'six', '７': 'seven',
    '８': 'eight', '９': 'nine', '０': 'zero', '１０': 'ten',
    '順位': 'rank', '◎': 'perfect', '○': 'great', '▲': 'soso', '△': 'bad', 'コード': 'code',
    '３Ｆ': 'three_F', "オッズ": "odds", "名": "name", "印": "mark",
    "指数": "index", "クラス": "class", "コメント": "comment", "距離": "distance", "コース": "course",
    "タイプ": "type", "フラグ": "flag", "データ": "data",
    "レース": "race", "レースキー": "racekey", "グレード": "grade", "ペース": "pace", "レースペース": "racepace",
    "コーナー": "corner", "ペースアップ": "paceup", "レースコメント": "racecomment", "キー": "key",
}) -> str:
    for o, n in prechar.items():
        jp = jp.replace(o, n)

    return "_".join(filter(
        lambda word: word != "",
        map(lambda item: endict[item['orig']] if item['orig'] in endict.keys()
            else item['hepburn'].strip(),
            kks.convert(jp))
    ))
