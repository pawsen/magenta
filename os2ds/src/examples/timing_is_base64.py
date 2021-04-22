#!/usr/bin/env python3

from functools import wraps
from time import time
from typing import Callable, TypeVar, cast, Any, Union

from base64 import b64decode, b64encode
import binascii
import re
from faker import Faker

"""Time different implementations of base64 check"""


F = TypeVar('F', bound=Callable[..., Any])
def timing(func: F) -> F:
    """
    @timing
    def f(a):
        for _ in range(a):
            i = 0
        return -1

    f(100000000)
    > func:'f' args:[(100000000,), {}] took: 14.2240 sec
    """
    @wraps(func)
    def wrap(*args, **kw):
        ts = time() * 1000
        result = func(*args, **kw)
        te = time() * 1000
        print('func:{0!r}, len string: {1:.2e}, took: {2:.4f} ms, return: {3!s}'.format(
          func.__name__, len(args[0]),te-ts, bool(result)))
        return result
    return cast(F, wrap)


@timing
def is_base64_encode_decode(sb: Union[str, bytes]) -> bool:
    """Test if a string or byte object appears to be Base64 encoded"""
    try:
        if isinstance(sb, str):
            # If there's any unicode here, an exception will be thrown and the
            # function will return false
            sb_bytes = bytes(sb, 'ascii')
        elif isinstance(sb, bytes):
            sb_bytes = sb
        else:
            raise ValueError("Argument must be string or bytes")
        return b64encode(b64decode(sb_bytes, validate=True)) == sb_bytes
    except Exception:
        return False


@timing
def is_base64_regex_compile(sb):
    try:
        if isinstance(sb, str):
            # If there's any unicode here, an exception will be thrown and the
            # function will return false
            sb_bytes = bytes(sb, 'ascii')
        elif isinstance(sb, bytes):
            sb_bytes = sb
        else:
            raise ValueError("Argument must be string or bytes")

        if not sb_bytes or len(sb_bytes) < 1:
            return False
        else:
            pattern = re.compile(b"^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{4}|[A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)$")
            return pattern.match(sb_bytes)
    except Exception:
        return False

@timing
def is_base64_regex(sb_bytes):
    try:
        if not sb_bytes or len(sb_bytes) < 1:
            return False
        else:
            pattern = b"^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{4}|[A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)$"
            return re.match(pattern, sb_bytes)
    except Exception:
        return False

@timing
def is_base64_decode(sb):
    try:
        if isinstance(sb, str):
            # If there's any unicode here, an exception will be thrown and the
            # function will return false
            sb_bytes = bytes(sb, 'ascii')
        elif isinstance(sb, bytes):
            sb_bytes = sb
        else:
            raise ValueError("Argument must be string or bytes")

        b64decode(sb_bytes, validate=True)
        return True
    except binascii.Error:
        return False

fake = Faker()
Faker.seed(4321)

# base64 encoded
for nchar in (1e3, 1e5, 1e7):
    s = fake.text(max_nb_chars=int(nchar))
    sb = b64encode(s.encode())
    print("base64 encoded")
    is_base64_encode_decode(sb)
    is_base64_regex_compile(sb)
    is_base64_regex(sb)
    is_base64_decode(sb)

# NOT base64 encoded
for nchar in (1e3, 1e5, 1e7):
    s = fake.text(max_nb_chars=int(nchar))
    sb = s.encode()
    print("NOT base64 encoded")
    is_base64_encode_decode(sb)
    is_base64_regex_compile(sb)
    is_base64_regex(sb)
    is_base64_decode(sb)
