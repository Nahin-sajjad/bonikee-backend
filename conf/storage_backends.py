from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    location = 'media'
    file_overwrite = False  # Set to True if you want to overwrite existing files


class StaticStorage(S3Boto3Storage):
    location = 'static'
    file_overwrite = True  # Set to True if you want to overwrite existing static files
