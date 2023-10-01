from PIL import Image, ImageOps
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage as storage
from apps.share.services.tenant_error_logger import TenantLogger
from apps.share.request_middleware import request_local


def image_processing(s3_path, target_size_kb=55, format="JPEG"):
    request = getattr(request_local, "request", None)
    tenant_logger = TenantLogger(request)
    # Validate input parameters
    if target_size_kb <= 0:
        raise ValueError("Target size must be greater than zero.")

    # Load the image from S3 storage
    try:
        image_file = storage.open(s3_path)
    except FileNotFoundError:
        tenant_logger.error(f"File not found at S3 path: {s3_path}")
        return None

    processed_image = Image.open(image_file)

    max_quality = 95  # Adjust as needed
    size = 1000

    # Initialize variables
    quality = max_quality

    # Define the maximum number of optimization iterations
    max_iterations = 20

    for iteration in range(max_iterations):
        buffer = BytesIO()

        # Convert the image to RGB mode before saving as JPEG
        rgb_image = ImageOps.exif_transpose(processed_image.convert("RGB"))

        rgb_image.save(buffer, format=format, quality=quality)
        image_size_kb = len(buffer.getvalue()) / 1024

        if image_size_kb <= target_size_kb:
            # Overwrite the original image in S3
            try:
                storage.delete(s3_path)
                storage.save(s3_path, ContentFile(buffer.getvalue()))
                return s3_path  # Return the path of the overwritten image in S3
            except Exception as e:
                tenant_logger.error(f"Error saving image to S3: {e}")
                return None
        else:
            processed_image = processed_image.resize((size, size))
            size -= 100

        # Reduce quality for the next iteration
        quality -= 5  # You can adjust this step size as needed

    tenant_logger.error(
        "Maximum optimization iterations reached. Target size not achieved."
    )
    return None