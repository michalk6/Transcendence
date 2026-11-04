from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models


# uploaded avatars live outside of the code, in a docker volume (see docker-compose.yml)
AVATAR_DIR = settings.BASE_DIR / "media" / "avatars"
avatar_storage = FileSystemStorage(location=AVATAR_DIR)


class Avatar(models.Model):
    user = models.OneToOneField(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="avatar",
    )
    file_name = models.CharField(max_length=100)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"avatar of {self.user}"
