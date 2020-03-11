import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG',
                    fmt='%(asctime)s.%(msecs)03d %(levelname)7s %(thread)5d --- [%(threadName)16s] %(funcName)-20s: %(message)s',
                    field_styles={'asctime': {'color': ''}, 'thread': {'color': 'magenta'},
                                  'funcName': {'color': 'cyan'}}
                    )
logging.addLevelName(logging.DEBUG, "\033[0;33m%8s\033[1;0m" % logging.getLevelName(logging.DEBUG))
logging.addLevelName(logging.INFO, "\033[0;33m%8s\033[1;0m" % logging.getLevelName(logging.INFO))
logging.addLevelName(logging.WARNING, "\033[0;33m%8s\033[1;0m" % logging.getLevelName(logging.WARNING))
logging.addLevelName(logging.ERROR, "\033[0;31m%8s\033[1;0m" % logging.getLevelName(logging.ERROR))
logging.addLevelName(logging.CRITICAL, "\033[0;31m%8s\033[1;0m" % logging.getLevelName(logging.CRITICAL))
