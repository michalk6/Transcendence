from io import BytesIO
from PIL import Image
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from apps.avatars.models import Avatar, avatar_storage


User = get_user_model()
ME_URL = "/api/avatars/me/"


def make_image_file(image_format="PNG", size=(400, 300), name="pic.png"):
    buffer = BytesIO()
    Image.new("RGB", size, "red").save(buffer, format=image_format)
    return SimpleUploadedFile(name, buffer.getvalue())


class AvatarTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("anna", "anna@example.com", "pass12345!")

    def tearDown(self):
        avatar = Avatar.objects.filter(user=self.user).first()
        if avatar is not None:
            avatar_storage.delete(avatar.file_name)

    def test_default_avatar_when_none_uploaded(self):
        response = self.client.get("/api/avatars/anna/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/svg+xml")

    def test_unknown_user_gives_404(self):
        response = self.client.get("/api/avatars/nobody/")
        self.assertEqual(response.status_code, 404)

    def test_upload_requires_login(self):
        response = self.client.put(ME_URL, {"avatar": make_image_file()}, format="multipart")
        self.assertEqual(response.status_code, 401)

    def test_upload_and_download(self):
        self.client.force_authenticate(self.user)
        response = self.client.put(ME_URL, {"avatar": make_image_file()}, format="multipart")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/api/avatars/anna/")
        self.assertEqual(response["Content-Type"], "image/png")
        image = Image.open(BytesIO(b"".join(response.streaming_content)))
        self.assertEqual(image.size, (256, 256))

    def test_second_upload_replaces_first(self):
        self.client.force_authenticate(self.user)
        self.client.put(ME_URL, {"avatar": make_image_file()}, format="multipart")
        self.client.put(ME_URL, {"avatar": make_image_file(size=(50, 50))}, format="multipart")
        self.assertEqual(Avatar.objects.filter(user=self.user).count(), 1)

    def test_not_an_image_is_rejected(self):
        self.client.force_authenticate(self.user)
        fake = SimpleUploadedFile("virus.png", b"this is not an image")
        response = self.client.put(ME_URL, {"avatar": fake}, format="multipart")
        self.assertEqual(response.status_code, 400)

    def test_gif_is_rejected(self):
        self.client.force_authenticate(self.user)
        gif = make_image_file(image_format="GIF", name="pic.gif")
        response = self.client.put(ME_URL, {"avatar": gif}, format="multipart")
        self.assertEqual(response.status_code, 400)

    def test_too_big_file_is_rejected(self):
        self.client.force_authenticate(self.user)
        big = SimpleUploadedFile("big.png", b"0" * (2 * 1024 * 1024 + 1))
        response = self.client.put(ME_URL, {"avatar": big}, format="multipart")
        self.assertEqual(response.status_code, 400)

    def test_delete_returns_default(self):
        self.client.force_authenticate(self.user)
        self.client.put(ME_URL, {"avatar": make_image_file()}, format="multipart")
        response = self.client.delete(ME_URL)
        self.assertEqual(response.status_code, 204)
        response = self.client.get("/api/avatars/anna/")
        self.assertEqual(response["Content-Type"], "image/svg+xml")
