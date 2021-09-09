from typing import List, Tuple
from dataclasses import dataclass

ColumnList = List[str]


@dataclass
class TableConfig:
    name: str
    primaryKey: ColumnList
    generatedColumns: List[str]
    indexes: List[Tuple[str, ColumnList]]


RaceKeyColumns = ["racekey"]
raceKeyWithHorseNumColumns = ["racekey", "umaban"]
kyousouseisekiKeyColumns = ["kyousouseisekikey"]

raceKeyGeneratedColumn = "racekey INT AS"\
    " (racekey_nen*1000000 + racekey_kai*100000 + "\
    "racekey_nichi*10000 + racekey_R*100 + racekey_ba_code) "\
    "STORED NOT NULL"
kyousouseisekiKeyGeneratedColumn = "kyousouseisekikey AS "\
    "(CONCAT(kyousouseiseki_key_kettou_tourokubangou, kyousouseiseki_key_nengappi)) "\
    "STORED"


TableConfigs = {
    "bac": TableConfig("bac", RaceKeyColumns, [raceKeyGeneratedColumn], []),
    "cha": TableConfig("cha", raceKeyWithHorseNumColumns, [raceKeyGeneratedColumn], []),
    "cyb": TableConfig("cyb", raceKeyWithHorseNumColumns, [raceKeyGeneratedColumn], []),
    "kka": TableConfig("kka", raceKeyWithHorseNumColumns, [raceKeyGeneratedColumn], []),
    "kyi": TableConfig("kyi", raceKeyWithHorseNumColumns, [raceKeyGeneratedColumn], []),
    "oz": TableConfig("oz", RaceKeyColumns, [raceKeyGeneratedColumn], []),
    "sed": TableConfig("sed", raceKeyWithHorseNumColumns, [raceKeyGeneratedColumn], []),
    "tyb": TableConfig("tyb", raceKeyWithHorseNumColumns, [raceKeyGeneratedColumn], []),
    "ukc": TableConfig("ukc", ["kettou_tourokubangou"], [raceKeyGeneratedColumn], []),
}
