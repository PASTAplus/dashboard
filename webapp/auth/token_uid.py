#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: token_uid

:Synopsis:

:Author:
    servilla

:Created:
    5/24/18
"""
import base64

import daiquiri
import nacl.encoding
import nacl.signing
import pendulum


logger = daiquiri.getLogger('token_uid: ' + __name__)


def is_expired(ttl=None):
    expired = False
    ts = pendulum.fromtimestamp(float(ttl))
    ts_add = ts.add(minutes=60).timestamp()
    now = pendulum.now().timestamp()
    if  ts_add <= now:
        expired = True
    return expired


def is_valid(token=None):
    token = base64.b64decode(token)
    signed_token = base64.b64decode(token.decode().split(':')[0].encode())
    verify_key_hex = token.decode().split(':')[1].encode()
    verify_key = nacl.signing.VerifyKey(verify_key_hex, encoder=nacl.encoding.HexEncoder)
    token_str = verify_key.verify(signed_token).decode()
    uid = token_str.split(',')[0]
    ttl = token_str.split(',')[1]
    if is_expired(ttl=ttl):
        msg = 'Expired token TTL'
        raise TTLException(msg)
    return uid


def to_token(uid=None):
    token = None
    signing_key = nacl.signing.SigningKey.generate()
    verify_key = signing_key.verify_key
    verify_key_hex = verify_key.encode(encoder=nacl.encoding.HexEncoder)
    token_ts = str(pendulum.now().timestamp())
    token_str = (uid + ',' + token_ts).encode()
    signed_token = base64.b64encode(signing_key.sign(token_str))
    token = base64.b64encode(signed_token + b':' + verify_key_hex)
    return token


class TTLException(Exception):
    pass


def main():

    return 0


if __name__ == "__main__":
    main()
