import pykakasi
from typing import Dict, List, Type


class Field:
    name: str
    translatedName: str
    occ: int
    size: int
    docType: str
    pyType: Type
    pos: int
    comment: str
    ignored: bool

    def __init__(self, name: str, occ: int, size: int, docType: str, pos: int,
                 comment: str = "", ignored=False) -> None:
        self.name = name
        self.size = size
        self.occ = occ
        self.docType = docType
        self.pos = pos
        self.comment = name + " " + comment
        if self.occ > 1:
            self.comment += " repeated:%dtimes" % self.occ
        self.ignored = ignored
        self.translatedName = translate(name)
        self.pyType = str if docType[0] == 'X' else int

    def genProtoField(self, num: int) -> str:
        return "\t{repeated}{type} {name} = {num}; {comment}".format(
            repeated="repeated " if self.occ > 1 else "",
            type="string" if self.pyType == str else "int32",
            name=self.translatedName,
            num=num,
            comment="" if self.comment == "" else "//"+self.comment)

    def getIgnored(self) -> bool:
        return self.ignored

    def getOcc(self) -> int:
        return self.occ


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
    "コーナー": "corner", "ペースアップ": "paceup", "レースコメント": "racecomment"
}) -> str:
    for o, n in prechar.items():
        jp = jp.replace(o, n)

    return "_".join(filter(
        lambda word: word != "",
        map(lambda item: endict[item['orig']] if item['orig'] in endict.keys()
            else item['hepburn'].strip(),
            kks.convert(jp))
    ))
