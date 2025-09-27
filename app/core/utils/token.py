from datetime import UTC, datetime, timedelta

import jwt

TOKEN_EXPIRY_LEEWAY_SEC = 0


class TokenUtils:
    def __init__(self, secret_key: str, algorithm: str):
        self.__secret_key = secret_key
        self.__algorithm = algorithm

    def generate_token(
        self, payload: dict, token_type: str, expiry_sec: int
    ) -> tuple[str, datetime]:
        """make jwt token with payload, expiry and token type. use secret key to sign"""
        issued_at = datetime.now(UTC)
        expires_at = issued_at + timedelta(seconds=expiry_sec)
        token_payload = {
            "iat": issued_at,
            "exp": expires_at,
            "type": token_type,
            **payload,
        }

        token = jwt.encode(token_payload, self.__secret_key, algorithm=self.__algorithm)
        return token, issued_at

    def decode_token(self, token: str, verify_expiry: bool = True) -> dict:
        payload = jwt.decode(
            token,
            key=self.__secret_key,
            algorithms=[self.__algorithm],
            leeway=timedelta(seconds=TOKEN_EXPIRY_LEEWAY_SEC),
            verify_exp=verify_expiry,
        )
        return payload
