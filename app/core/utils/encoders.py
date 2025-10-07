from fastapi.encoders import jsonable_encoder as fastapi_jsonable_encoder


def safe_jsonable_encoder(obj, sqlalchemy_safe: bool = True):
    return fastapi_jsonable_encoder(obj, sqlalchemy_safe=sqlalchemy_safe)
