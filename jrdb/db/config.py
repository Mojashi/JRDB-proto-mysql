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
    "bac": TableConfig("Bac", RaceKeyColumns, [raceKeyGeneratedColumn], []),
    "cha": TableConfig("Cha", raceKeyWithHorseNumColumns, [raceKeyGeneratedColumn], []),
    "cyb": TableConfig("Cyb", raceKeyWithHorseNumColumns, [raceKeyGeneratedColumn], []),
    "kka": TableConfig("Kka", raceKeyWithHorseNumColumns, [raceKeyGeneratedColumn], []),
    "kyi": TableConfig("Kyi", raceKeyWithHorseNumColumns, [raceKeyGeneratedColumn], []),
    "oz": TableConfig("Oz", RaceKeyColumns, [raceKeyGeneratedColumn], []),
    "sed": TableConfig("Sed", raceKeyWithHorseNumColumns, [raceKeyGeneratedColumn], []),
    "tyb": TableConfig("Tyb", raceKeyWithHorseNumColumns, [raceKeyGeneratedColumn], []),
    "ukc": TableConfig("Ukc", ["kettou_tourokubangou"], [], []),
}
