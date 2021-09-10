from os import name
from typing import List, Tuple
from dataclasses import dataclass, field

ColumnList = List[str]


@dataclass
class TableConfig:
    name: str
    primaryKey: ColumnList
    generatedColumns: List[str] = field(default_factory=list)
    indexes: List[Tuple[str, ColumnList]] = field(default_factory=list)
    ignoreDuplicate: bool = False


RaceKeyColumns = ["racekey"]
raceKeyWithHorseNumColumns = ["racekey", "umaban"]
kyousouseisekiKeyColumns = ["kyousouseisekikey"]

raceKeyGeneratedColumn = "racekey INT AS"\
    " (racekey_nen*10000000 + racekey_kai*1000000 + "\
    "racekey_nichi*10000 + racekey_R*100 + racekey_ba_code) "\
    "STORED NOT NULL"
kyousouseisekiKeyGeneratedColumn = "kyousouseisekikey AS "\
    "(CONCAT(kyousouseiseki_key_kettou_tourokubangou, kyousouseiseki_key_nengappi)) "\
    "STORED"


TableConfigs = {
    "bac": TableConfig(name="Bac", primaryKey=RaceKeyColumns,
                       generatedColumns=[raceKeyGeneratedColumn], ignoreDuplicate=True),
    "cha": TableConfig(name="Cha", primaryKey=raceKeyWithHorseNumColumns,
                       generatedColumns=[raceKeyGeneratedColumn]),
    "cyb": TableConfig(name="Cyb", primaryKey=raceKeyWithHorseNumColumns,
                       generatedColumns=[raceKeyGeneratedColumn], ignoreDuplicate=True),
    "kka": TableConfig(name="Kka", primaryKey=raceKeyWithHorseNumColumns,
                       generatedColumns=[raceKeyGeneratedColumn]),
    "kyi": TableConfig(name="Kyi", primaryKey=raceKeyWithHorseNumColumns,
                       generatedColumns=[raceKeyGeneratedColumn]),
    "oz": TableConfig(name="Oz", primaryKey=RaceKeyColumns,
                      generatedColumns=[raceKeyGeneratedColumn]),
    "sed": TableConfig(name="Sed", primaryKey=raceKeyWithHorseNumColumns,
                       generatedColumns=[raceKeyGeneratedColumn]),
    "tyb": TableConfig(name="Tyb", primaryKey=raceKeyWithHorseNumColumns,
                       generatedColumns=[raceKeyGeneratedColumn], ignoreDuplicate=True),
    "ukc": TableConfig(name="Ukc", primaryKey=["kettou_tourokubangou"],
                       ignoreDuplicate=True),
}
