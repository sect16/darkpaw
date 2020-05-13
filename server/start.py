#!/usr/bin/python
# Description : DarkPaw client
# E-mail      : sect16@gmail.com
# Author      : Chin Pin Hon
# Date        : 14.01.2020
# 

import logging.config
import os

import yaml

import server

if __name__ == '__main__':
    logging.addLevelName(logging.DEBUG, "\033[0;32m%8s\033[1;0m" % logging.getLevelName(logging.DEBUG))
    logging.addLevelName(logging.INFO, "\033[0;32m%8s\033[1;0m" % logging.getLevelName(logging.INFO))
    logging.addLevelName(logging.WARNING, "\033[0;33m%8s\033[1;0m" % logging.getLevelName(logging.WARNING))
    logging.addLevelName(logging.ERROR, "\033[0;31m%8s\033[1;0m" % logging.getLevelName(logging.ERROR))
    logging.addLevelName(logging.CRITICAL, "\033[0;31m%8s\033[1;0m" % logging.getLevelName(logging.CRITICAL))
    with open(str(os.getcwd()) + "/logging.yaml", "r") as f:
        logConfig = yaml.safe_load(f.read())
    logging.config.dictConfig(logConfig)
    while True:
        server.main()
