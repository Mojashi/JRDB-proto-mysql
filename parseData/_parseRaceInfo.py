from typing import Dict, Iterable, Mapping, Set
from config import RaceInfoDtypes
import os
from .parser import DTInfo, parseData
from utils import getDateFromL2Date, getDtypeDataDir,\
    isEveryHorseInfo, splitTxtName, writeMutipleProto
from env import DataDir
from config import DtypeDescs
from parseDoc import getDataType
import glob
import proto.build.raceinfo_pb2 as raceinfo_pb2


def convDay(day: str, dtinfos: Mapping[str, DTInfo]) -> Iterable[raceinfo_pb2.RaceInfo]:
    infos: Dict[int, raceinfo_pb2.RaceInfo] = {}

    for dtname, dtinfo in dtinfos.items():
        fname = DataDir + "/" + dtname.lower() + "/" + dtname.upper() + day + ".txt"
        protoT, dtype, convs, isEvery = dtinfo
        try:
            with open(fname, "rb", 100000) as f:
                datas = parseData(protoT, dtype, convs, f)
                for d in datas:
                    bacode = getattr(d, "racekey_ba_code")
                    nen = getattr(d, "racekey_nen")
                    kai = getattr(d, "racekey_kai")
                    nichi = getattr(d, "racekey_nichi")
                    r = getattr(d, "racekey_R")
                    racekey = nen*10000000 + kai*1000000 + nichi*1000 + r*100 + bacode
                    if racekey not in infos:
                        infos[racekey] = raceinfo_pb2.RaceInfo()

                    if isEvery:
                        getattr(getattr(infos[racekey], dtname), "append")(d)
                    else:
                        getattr(getattr(infos[racekey],
                                dtname), "MergeFrom")(d)
        except FileNotFoundError:
            pass

    return infos.values()


def parseRaceInfo(outfname: str, dataDir: str = DataDir):
    dtinfos: Dict[str, DTInfo] = {}
    days: Set[str] = set()

    for dtypeName in RaceInfoDtypes:
        parentDtypeName = DtypeDescs[dtypeName.lower()].dataIncludedIn

        dtype = getDataType(dtypeName)
        fieldConvertors = dtype.fieldConvertors()
        ProtoT = getattr(getattr(raceinfo_pb2, dtypeName +
                         "__pb2"), dtypeName.capitalize())
        dtinfos[dtypeName] = (ProtoT, dtype, fieldConvertors,
                              isEveryHorseInfo(dtypeName))
        dir = getDtypeDataDir(parentDtypeName, dataDir)

        files = sorted(glob.glob(dir + "/%s*.txt" % dtypeName.upper()))
        days.update(map(lambda fname: splitTxtName(
            os.path.basename(fname))[1], files))

    with open(outfname, "wb") as f:
        for day in sorted(days, key=getDateFromL2Date):
            print(day)
            writeMutipleProto(convDay(day, dtinfos), f)
