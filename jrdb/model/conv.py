

from typing import Optional
import logging


def convStrType(s: bytes) -> str:
    return s.decode("cp932").strip()


def convSignedIntTypeDEC(s: bytes) -> Optional[int]:
    s = bytes(filter(lambda ch: ch != 0x20, s))
    try:
        return int(s, 10)
    except ValueError:
        if all(ch == 0x20 for ch in s):
            return None
        else:
            logging.warning("failed to parse bytes:%s into signed int", s.decode("cp932"))
            return None


def convSignedIntTypeHEX(s: bytes) -> Optional[int]:
    s = bytes(filter(lambda ch: ch != 0x20, s))
    try:
        return int(s, 16)
    except ValueError:
        if all(ch == 0x20 for ch in s):
            return None
        else:
            logging.warning("failed to parse bytes:%s into signed hex int", s.decode("cp932"))
            return None


def convIntTypeDEC(s: bytes) -> Optional[int]:
    try:
        return int(s, 10)
    except ValueError:
        if all(ch == 0x20 for ch in s):
            return None
        else:
            logging.warning("failed to parse bytes:%s into int", s.decode("cp932"))
            return None


def convIntTypeHEX(s: bytes) -> Optional[int]:
    try:
        return int(s, 16)
    except ValueError:
        if all(ch == 0x20 for ch in s):
            return None
        else:
            logging.warning("failed to parse bytes:%s into hex int", s.decode("cp932"))
            return None


def convSignedFloatType(s: bytes) -> Optional[float]:
    s = bytes(filter(lambda ch: ch != 0x20, s))
    try:
        return float(s)
    except ValueError:
        if all(ch == 0x20 for ch in s):
            return None
        else:
            logging.warning("failed to parse bytes:%s into hex int", s.decode("cp932"))
            return None


def convFloatType(s: bytes) -> Optional[float]:
    try:
        return float(s)
    except ValueError:
        if all(ch == 0x20 for ch in s):
            return None
        else:
            logging.warning("failed to parse bytes:%s into hex int", s.decode("cp932"))
            return None
