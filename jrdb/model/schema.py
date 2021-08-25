from typing import Dict, List, Type

class Field:
    name : str
    translatedName : str
    occ : int
    size : str
    docType : str
    pyType : Type
    pos:int
    comment:str
    def __init__(self, name:str, occ:int, size:int, docType:str, pos:int, comment:str = "") -> None:
        self.name = name
        self.size = size
        self.occ = occ
        self.docType = docType
        self.pos = pos
        self.comment = comment

        self.translatedName = translate(name)
        self.pyType = str if docType[0] == 'X' else int

    def genProtoField(self, num:int) -> str:
        return "\t%s %s = %d;" % ("string" if self.pyType == str else "int32", self.translatedName, num)

class DataType:
    dtname : str
    fields : List[Field]

    def __init__(self, dtname:str) -> None:
        self.dtname = dtname
        self.fields = []

    def genProto(self) -> str:
        fields = "\n".join(map(lambda ifield: ifield[1].genProtoField(ifield[0] + 1), enumerate(self.fields)))
        return 'syntax = "proto3";\nmessage SearchRequest {\n%s\n}' % fields

import pykakasi
kks = pykakasi.kakasi()


prechar = {'(':'かっこ', ')':'かっこ'}
def translate(jp:str, endict:Dict[str,str] = {
    '1':'one','2':'two','3':'three','4':'four','5':'five','6':'sic','7':'seven', '8':'eight','9':'nine','0':'zero','10':'ten',
    '１':'one','２':'two','３':'three','４':'four','５':'five','６':'six','７':'seven', '８':'eight','９':'nine','０':'zero','１０':'ten',
    '順位':'rank','◎':'perfect','○':'great','▲':'soso','△':'bad','コード':'code','３Ｆ':'three_F'
}) -> str:
    for o,n in prechar.items():
        jp = jp.replace(o,n)

    return "_".join(map(lambda item: endict[item['orig']] if item['orig'] in endict.keys() else item['hepburn'], kks.convert(jp)))