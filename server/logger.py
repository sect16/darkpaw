import coloredlogs
import yaml
import os
import logging.config

logging.addLevelName(logging.DEBUG, "\033[0;32m%8s\033[1;0m" % logging.getLevelName(logging.DEBUG))
logging.addLevelName(logging.INFO, "\033[0;32m%8s\033[1;0m" % logging.getLevelName(logging.INFO))
logging.addLevelName(logging.WARNING, "\033[0;33m%8s\033[1;0m" % logging.getLevelName(logging.WARNING))
logging.addLevelName(logging.ERROR, "\033[0;31m%8s\033[1;0m" % logging.getLevelName(logging.ERROR))
logging.addLevelName(logging.CRITICAL, "\033[0;31m%8s\033[1;0m" % logging.getLevelName(logging.CRITICAL))

f = open(str(os.getcwd()) + "/logging.yaml", "r")
logConfig = yaml.safe_load(f.read())
f.close()

coloredlogs.install()
logging.config.dictConfig(logConfig)
