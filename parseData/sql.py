

# def insertAllData(cur: CursorBase, dtypeName: str,
#                   dataDir: str = DataDir, protoBuildDir: str = ProtoBuildDir):
#     parentDtypeName = DtypeDescs[dtypeName.lower()].dataIncludedIn
#     dir = getDtypeDataDir(parentDtypeName, dataDir)

#     fromName = protoBuildDir.replace("/", ".")
#     pbModule = __import__(fromName + ".%s_pb2" %
#                           dtypeName, fromlist=[fromName])
#     dtype = getDataType(dtypeName)
#     fieldConvertors = dtype.fieldConvertors()
#     ProtoT = getattr(pbModule, dtype.dtname.capitalize())

#     sqlModule = __import__(fromName + ".%s_sqlhelper" %
#                            dtypeName, fromlist=[fromName])
#     insertConvFunc = getattr(sqlModule, "conv%sProtoClassToData" % dtypeName.capitalize())
#     columnList: List[str] = getattr(sqlModule, "get%sColumnNames" % dtypeName.capitalize())()

#     conf = TableConfigs[dtypeName]
#     ignore = "IGNORE" if conf.ignoreDuplicate else ""

#     files = sorted(glob.glob(dir + "/%s*.txt" % dtypeName.upper()))

#     que: queue.Queue = queue.Queue(100)

#     def processQueue(que: queue.Queue, outputFile: str):
#         with open(outputFile, "a") as f:
#             while True:
#                 rows = que.get()
#                 # finish signal
#                 if len(rows) == 0:
#                     return

#                 try:
#                     for value in map(lambda row: insertConvFunc(row), rows):
#                         for elem in value:
#                             if type(elem) == bytes:
#                                 f.write(elem.hex())
#                             elif elem is None:
#                                 f.write(r"\N")
#                             else:
#                                 f.write(str(elem))
#                             f.write("\t")
#                         f.write("\n")
#                 except Exception as e:
#                     with open("dump.log", "w") as f:
#                         for r in rows:
#                             f.write(json_format.MessageToJson(r))
#                     raise e

#     dataFileName = "/var/lib/mysql-files/loaddata.txt"

#     if os.path.exists(dataFileName):
#         os.remove(dataFileName)
#     th = threading.Thread(target=processQueue,
#                           args=(que, dataFileName), daemon=True)
#     th.start()

#     for fname in files:
#         logging.info(fname)
#         with open(fname, "rb", 100000) as f:
#             que.put(parseData(ProtoT, dtype, fieldConvertors, f))

#     que.put([])  # send finish signal
#     th.join()

#     logging.info("load data into DB")
#     cur.execute('LOAD DATA INFILE "%s" %s '
#                 'INTO TABLE %s (%s) SET PROTO_BINARY=UNHEX(@proto_binary)' %
#                 (dataFileName, ignore, dtypeName.capitalize(),
#                  ",".join(columnList[:-1] + ["@proto_binary"])))

# def checkEmpty(cur: CursorBase, tableName: str) -> bool:
#     cur.execute(f"SELECT 1 from {tableName} limit 1")
#     for _ in cur:
#         return False
#     return True
