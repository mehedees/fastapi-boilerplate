from datetime import UTC, datetime, timedelta
from enum import Enum

import jwt

TOKEN_EXPIRY_LEEWAY_SEC = 0


class TokenTypeEnum(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class TokenUtils:
    def __init__(
        self,
        access_token_secret_key: str,
        refresh_token_secret_key: str,
        algorithm: str,
    ):
        self.__access_token_secret_key = access_token_secret_key
        self.__refresh_token_secret_key = refresh_token_secret_key
        self.__algorithm = algorithm

    def __generate_token(
        self, payload: dict, token_type: str, expiry_sec: int, secret_key: str
    ) -> tuple[str, datetime]:
        """make jwt token with payload, expiry and token type. use secret key to sign"""
        issued_at = datetime.now(UTC)
        expires_at = issued_at + timedelta(seconds=expiry_sec)
        token_payload = {
            "iat": issued_at,
            "exp": expires_at,
            "token_type": token_type,
            **payload,
        }
        token = jwt.encode(token_payload, secret_key, algorithm=self.__algorithm)
        return token, issued_at

    def __decode_token(self, token: str, secret_key: str, verify_expiry: bool) -> dict:
        payload = jwt.decode(
            token,
            key=secret_key,
            algorithms=[self.__algorithm],
            leeway=timedelta(seconds=TOKEN_EXPIRY_LEEWAY_SEC),
            options={"verify_exp": verify_expiry},
        )
        return payload

    def generate_access_token(
        self, payload: dict, expiry_sec: int
    ) -> tuple[str, datetime]:
        return self.__generate_token(
            payload,
            TokenTypeEnum.ACCESS.value,
            expiry_sec,
            self.__access_token_secret_key,
        )

    def generate_refresh_token(
        self, payload: dict, expiry_sec: int
    ) -> tuple[str, datetime]:
        return self.__generate_token(
            payload,
            TokenTypeEnum.REFRESH.value,
            expiry_sec,
            self.__refresh_token_secret_key,
        )

    def decode_access_token(self, token: str, verify_expiry: bool = True) -> dict:
        return self.__decode_token(token, self.__access_token_secret_key, verify_expiry)

    def decode_refresh_token(self, token: str, verify_expiry: bool = True) -> dict:
        return self.__decode_token(
            token, self.__refresh_token_secret_key, verify_expiry
        )
