# -*- coding: utf-8 -*-

import jwt
import hashlib
from uuid import uuid1
from time import time

from functools import wraps
from flask import request, g, abort


def generate_uid():
    return hashlib.md5(bytes(str(uuid1()) + str(time()), "utf-8")).hexdigest()


def decode_json(token):
    return jwt.decode(token, '4ae5', algorithm='HS256')


def encode_json(token):
    return jwt.encode(token, '4ae5', algorithm='HS256')


def authorization(view_func):
    @wraps(view_func)
    def decorated_function(*args, **kwargs):
        authorization = request.headers.get("Authorization")
        if authorization:
            token = authorization.split()[-1]
            # print(token)
            # try:
            """
            {
                "user_id": String,
                "party": List,
                "engine_config": dict
            }
            """
            g.token = decode_json(token)
            g.token["user_id"]
            return view_func(*args, **kwargs)
            # except Exception as e:
            #     print(e)
        return abort(404)
    return decorated_function


if __name__ == '__main__':
    # print(_md5("12345678"))
    # print(encode_json({"a": 1}))
    # print(decode_json(bytes("eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhIjoxfQ.zyz6EmjQbUlYjDqMCfT8dLNvU6_bDlAKGBdfFJdkS7g", encoding="utf-8")))
    print(jwt.decode("eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhIjoxfQ.zyz6EmjQbUlYjDqMCfT8dLNvU6_bDlAKGBdfFJdkS7g1", '4ae5', algorithm='HS256'))
    # 25d55ad283aa400af464c76d713c07ad
