from django.core.files.storage import default_storage as storage
from apps.share.services.tenant_error_logger import TenantLogger
from apps.share.request_middleware import request_local


def storage_image_delete(s3_path):
    request = getattr(request_local, "request", None)
    tenant_logger = TenantLogger(request)

    try:
        storage.delete(s3_path)
        print(s3_path)
    except Exception as e:
        print(e)
        tenant_logger.error(f"Error deleting image from S3: {e}")
        return None
