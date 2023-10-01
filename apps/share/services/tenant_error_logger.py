import logging


class TenantLogger:
    def __init__(self, request):
        self.request = request
        print(request.tenant)
        self.logger = logging.getLogger(f"tenant_{self.request.tenant}")

    def warning(self, e):
        self.logger.warning(
            e, extra={"method": self.request.method, "path": self.request.path}
        )

    def error(self, e):
        self.logger.error(
            e, extra={"method": self.request.method, "path": self.request.path}
        )

    def debug(self, e):
        self.logger.debug(
            e, extra={"method": self.request.method, "path": self.request.path}
        )

    def info(self, e):
        self.logger.info(
            e, extra={"method": self.request.method, "path": self.request.path}
        )
