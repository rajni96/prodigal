import logging
import os
import datetime


class MyLogger:
    _logger = None

    def __new__(cls, *args, **kwargs):
        if cls._logger is None:

            print("Logger new")
            cls._logger = super().__new__(cls, *args, **kwargs)
            cls._logger = logging.getLogger()
            # cls._logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

            streamHandler = logging.StreamHandler()

            streamHandler.setFormatter(formatter)

            cls._logger.addHandler(streamHandler)

        return cls._logger
