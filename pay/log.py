
import logging
from logging.handlers import TimedRotatingFileHandler


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

        fh = TimedRotatingFileHandler("info.log", when="D", interval=1, backupCount=30)

        fh.setFormatter(fmt)

        fh.setLevel(Flevel)

        self.logger.addHandler(sh)

        self.logger.addHandler(fh)

    def __getattr__(self, item):
        return getattr(self.logger, item)

