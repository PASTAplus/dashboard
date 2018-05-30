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
import os

import daiquiri
import nacl.encoding
import nacl.signing
import nacl.hash
import pendulum


logger = daiquiri.getLogger('token_uid: ' + __name__)


def is_expired(ttl=None):
    expired = False
    timestamp = pendulum.fromtimestamp(float(ttl))
    future = timestamp.add(minutes=30).timestamp()
    now = pendulum.now().timestamp()
    if  future <= now:
        expired = True
    return expired


def decode_uid(token=None):
    uid = None
    token_file = './tokens/' + token
    with open(token_file, 'rb') as t:
        token_pair = t.read().decode()
    uid, ttl = token_pair.split(',')
    if is_expired(ttl=ttl):
        remove_token(token=token)
        raise TTLException()
    return uid


def remove_token(token=None):
    try:
        token_file = './tokens/' + token
        os.remove(token_file)
    except Exception as e:
        logger.error(e)


def to_token(uid=None):
    HASHER = nacl.hash.sha256
    timestamp = str(pendulum.now().timestamp())
    token_pair = (uid + ',' + timestamp).encode()
    token = HASHER(token_pair, encoder=nacl.encoding.HexEncoder)
    token_file = './tokens/' + token.decode()
    with open(token_file, 'wb') as t:
        t.write(token_pair)
    return token


class TTLException(Exception):
    pass


def main():

    return 0


if __name__ == "__main__":
    main()
