"""This module contains the GeneFlow Logging class."""

import logging
import  sys


class Log:
    """Log events while running GeneFlow workflows."""

    LOGLEVEL = {
        'debug'   : logging.DEBUG,
        'info'    : logging.INFO,
        'warning' : logging.WARNING,
        'error'   : logging.ERROR,
        'critical': logging.CRITICAL
    }

    # class level logger
    logger = logging.getLogger('GeneFlow')

    @classmethod
    def config(cls, log_level, log_file):
        """
        Configure global logging params.

        Args:
            cls: class instance.
            log_level: logging level.
            log_file: log output file, STDOUT if not specified.

        Returns:
            False

        """
        log_format = (
            '%(asctime)s %(levelname)s '
            '[%(filename)s:%(lineno)d:%(funcName)s()] %(message)s'
        )
        formatter = logging.Formatter(
            fmt=log_format, datefmt='%Y-%m-%d %H:%M:%S'
        )

        # set log handler to either stdout or append file
        handler = None
        if log_file:
            handler = logging.FileHandler(log_file, mode='a')
        else:
            handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)

        cls.logger.addHandler(handler)
        cls.logger.setLevel(cls.LOGLEVEL.get(log_level, logging.INFO))


    @classmethod
    def a(cls):
        """
        Ensure current frame is properly reported.

        Args:
            cls: class instance.

        Returns:
            logger class instance.

        """
        return cls.logger

    @classmethod
    def an(cls):
        """
        Ensure current frame is properly reported.

        Args:
            cls: class instance.

        Returns:
            logger class instance.

        """
        return cls.logger

    @classmethod
    def some(cls):
        """
        Ensure current frame is properly reported.

        Args:
            cls: class instance.

        Returns:
            logger class instance.

        """
        return cls.logger
