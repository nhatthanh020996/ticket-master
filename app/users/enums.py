from enum import StrEnum, IntEnum

class IGenderEnum(StrEnum):
    female = "female"
    male = "male"
    other = "other"


class IRoleEnum(IntEnum):
    SUPER_ADMIN = 1
    ADMIN = 2
    NORMAL_USER = 3
