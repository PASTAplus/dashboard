# -*- coding: utf-8 -*-

""":Mod: run

:Synopsis:

:Author:
    servilla

:Created:
    2/15/18
"""
from webapp import app
from config import Config

if __name__ == '__main__':
    app.config.from_object(Config)
    app.run()
