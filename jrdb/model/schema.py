from typing import List, Type


class Field:
    name : str
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

        self.pyType = str if docType[0] == 'X' else int

    def genProtoField(self, num:int) -> str:
        return "\t%s %s = %d;" % ("string" if self.pyType == str else "int32", self.name, num)

class DataType:
    dtname : str
    fields : List[Field]

    def __init__(self, dtname:str) -> None:
        self.dtname = dtname
        self.fields = []

    def genProto(self) -> str:
        fields = "\n".join(map(lambda ifield: ifield[1].genProtoField(ifield[0] + 1), enumerate(self.fields)))
        return 'syntax = "proto3";\nmessage SearchRequest {\n%s\n}' % fields
