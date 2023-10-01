import logging
import os
from django.db import connection
from django_tenants.middleware import TenantMiddleware

class TenantLoggerMiddleware(TenantMiddleware):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the current tenant
        tenant = connection.tenant

        # Configure logging for the current tenant
        self.configure_logging(tenant)

        try:
            response = self.get_response(request)
        except Exception as e:
            # Log the exception
            logger = logging.getLogger(f'tenant_{tenant}')
            logger.error("An error occurred: %s", str(e))
            raise  # Re-raise the exception

        return response

    def configure_logging(self, tenant):
        # Define a logger specific to the tenant
        logger = logging.getLogger(f'tenant_{tenant}')
        logger.setLevel(logging.DEBUG)

        # Get the log file path
        if not os.path.exists('tenant_logs'):
            os.mkdir('tenant_logs')
        log_file_path = os.path.join('tenant_logs', f'{tenant}.log')

        # Check if the log file exists; if not, create it
        if not os.path.exists(log_file_path):
            with open(log_file_path, 'w'):
                pass

        # Configure a FileHandler for this logger
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(logging.DEBUG)

        # Create a formatter for the log messages
        formatter = logging.Formatter(
            '{levelname} {asctime} {message} [Method: {method}, Path: {path}]',
            style='{'
        )

        # Set the formatter for the file handler
        file_handler.setFormatter(formatter)

        # Add the file handler to the logger
        logger.addHandler(file_handler)