from enum import StrEnum


class TokenType(StrEnum):
    ACCESS = "access_token"
    REFRESH = "refresh_token"