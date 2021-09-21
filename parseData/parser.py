from model.schema import Convertor, DataType
from typing import IO, Any, List, Tuple
import logging


def parseData(ProtoT, dtype: DataType,
              fieldConvertors: List[Convertor], data: IO) -> List[Any]:

    def parseRow():
        ret = ProtoT()
        for field, convType in zip(dtype.fields, fieldConvertors):
            try:
                for _ in range(field.occ):
                    s = data.read(field.size)
                    if field.originalName == "改行" and s != b"\r\n":
                        raise Exception("invalid format!!!")
                    if not s:
                        return None

                    if not field.ignored:
                        try:
                            v = convType(s)
                        except Exception as e:
                            logging.error(e.args)
                            logging.error("field: " + field.originalFullName)
                            v = None

                        if field.occ == 1:
                            if v is None:
                                continue
                            setattr(ret, field.translatedName, v)
                        else:
                            getattr(getattr(ret, field.translatedName), "append")(
                                v if v is not None else 0)
            except Exception as e:
                raise Exception(field.originalFullName) from e
        return ret

    rows = []
    while True:
        row = parseRow()
        if row is None:
            break
        rows.append(row)

    return rows


DTInfo = Tuple[Any, DataType, List[Convertor], bool]
