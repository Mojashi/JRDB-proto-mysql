from env import DataDir


def getDtypeDataDir(dtypeName: str, dataDir: str = DataDir):
    return dataDir + "/" + dtypeName.lower()
