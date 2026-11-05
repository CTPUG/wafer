from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible


@deconstructible
class PrivateTalkStorage(FileSystemStorage):
    """Store talk attachments outside the publicly served media directory."""

    def __init__(self):
        super().__init__(location=settings.PRIVATE_MEDIA_ROOT)
