import logging


class ServerLogger:
    def __init__(self):
        self.error_logger = logging.getLogger("error")

    def error(self, e):
        self.error_logger.error(e)
