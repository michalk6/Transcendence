from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from rest_framework.exceptions import ValidationError
from apps.avatars.models import Avatar, avatar_storage


MAX_UPLOAD_SIZE = 2 * 1024 * 1024
ALLOWED_FORMATS = ["JPEG", "PNG", "WEBP"]
AVATAR_SIDE = 256


def check_upload_size(uploaded_file):
    if uploaded_file.size > MAX_UPLOAD_SIZE:
        raise ValidationError({"avatar": "File is too big (max 2 MB)."})


def open_image(uploaded_file):
    try:
        image = Image.open(uploaded_file)
        image.load()
    except Exception:
        raise ValidationError({"avatar": "File is not a valid image."})
    if image.format not in ALLOWED_FORMATS:
        raise ValidationError({"avatar": "Allowed formats: JPEG, PNG, WEBP."})
    return image


def crop_to_square(image):
    width, height = image.size
    side = min(width, height)
    left = (width - side) // 2
    top = (height - side) // 2
    return image.crop((left, top, left + side, top + side))


def encode_avatar(image):
    # the image is saved again from pixels only, so metadata (EXIF, GPS) and any hidden payload are dropped
    image = image.convert("RGBA")
    image = crop_to_square(image)
    image = image.resize((AVATAR_SIDE, AVATAR_SIDE))
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue())


def remove_old_file(avatar):
    if avatar.file_name and avatar_storage.exists(avatar.file_name):
        avatar_storage.delete(avatar.file_name)


def get_or_create_avatar(user):
    avatar = Avatar.objects.filter(user=user).first()
    if avatar is None:
        avatar = Avatar(user=user)
    return avatar


def save_avatar(user, uploaded_file):
    check_upload_size(uploaded_file)
    image = open_image(uploaded_file)
    content = encode_avatar(image)

    avatar = get_or_create_avatar(user)
    remove_old_file(avatar)
    avatar.file_name = avatar_storage.save(f"{user.pk}.png", content)
    avatar.save()
    return avatar


def delete_avatar(user):
    avatar = Avatar.objects.filter(user=user).first()
    if avatar is None:
        return
    remove_old_file(avatar)
    avatar.delete()
