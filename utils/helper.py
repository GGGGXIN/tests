import base64
import structlog
import logging
import os
from logging.handlers import TimedRotatingFileHandler

from flask.json import JSONEncoder as BaseJSONEncoder
# from Crypto.Cipher import AES
import re
# pycryptotodome

# class AESCoder:
#     def __init__(self, key):
#         self.key = key
#
#     def encrypt(self, data):
#         BS = 16
#         iv = self.key[0:16]
#         pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
#         raw = pad(data)
#         cipher = AES.new(self.key, AES.MODE_CBC, iv)
#         return base64.b64encode(cipher.encrypt(raw))


class Logger:

    def __init__(self, path, clevel=logging.DEBUG, Flevel=logging.DEBUG):
        self.logger = logging.getLogger(path)

        self.logger.setLevel(logging.DEBUG)

        fmt = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')

        # 设置CMD日志

        sh = logging.StreamHandler()

        sh.setFormatter(fmt)

        sh.setLevel(clevel)

        # 设置文件日志

        fh = TimedRotatingFileHandler("logs/info.log", when="D", interval=1, backupCount=30)

        fh.setFormatter(fmt)

        fh.setLevel(Flevel)

        self.logger.addHandler(sh)

        self.logger.addHandler(fh)

    def __getattr__(self, item):
        return getattr(self.logger, item)

