from typing import List, Type


class Field:
    name : str
    docType : str
    pyType : Type
    

class DataType:
    dtname : str
    fields : List[Field]

    def genProto(self) -> str:
        pass
