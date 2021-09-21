# may be master data
from posixpath import basename
from .parser import parseData
from parseDoc import getDataType
from env import DataDir, ProtoBuildDir
import glob
from utils import getDateFromL2Date, getDtypeDataDir, splitTxtName, writeMutipleProto
from config import DtypeDescs, DtypeID  # noqa: E402


def parseIndivisual(outfname: str,
                    dtypeName: DtypeID, dataDir: str = DataDir,
                    protoBuildDir: str = ProtoBuildDir):
    assert(dtypeName in DtypeDescs.keys())

    fromName = protoBuildDir.replace("/", ".")
    pbModule = __import__(fromName + ".%s_pb2" %
                          dtypeName, fromlist=[fromName])
    ProtoT = getattr(pbModule, dtypeName.capitalize())

    dtype = getDataType(dtypeName)
    fieldConvertors = dtype.fieldConvertors()
    parentDtypeName = DtypeDescs[dtypeName.lower()].dataIncludedIn
    dir = getDtypeDataDir(parentDtypeName, dataDir)

    files = sorted(glob.glob(dir + "/%s*.txt" % dtypeName.upper()),
                   key=lambda fname: getDateFromL2Date(splitTxtName(basename(fname))[1]))

    with open(outfname, "wb") as outf:
        for file in files:
            print(file)
            with open(file, "rb", 1000000) as f:
                writeMutipleProto(
                    parseData(ProtoT, dtype, fieldConvertors, f), 
                    outf)
