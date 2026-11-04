from django.utils import timezone
from redis import asyncio
from django.conf import settings
from apps.users.models import User
import json


MESSAGES_LIMIT = 100
GENERAL_CHAT_MESSAGE_LIST = "general_chat_message_list"
redis_client = asyncio.from_url(settings.REDIS_URL)


async def save_general_message(user: User, content: str) -> dict:
    message = {
        "sender": {"id": user.pk, "username": user.username},
        "content": content,
        "created_at": timezone.now().isoformat()
    }
    message_json = json.dumps(message)
    await redis_client.rpush(GENERAL_CHAT_MESSAGE_LIST, message_json)
    await redis_client.ltrim(GENERAL_CHAT_MESSAGE_LIST, -MESSAGES_LIMIT, -1)
    return message


async def get_general_message_list() -> list[dict]:
    json_list = await redis_client.lrange(
        GENERAL_CHAT_MESSAGE_LIST, 0, -1
    )
    general_message_list = [json.loads(j) for j in json_list]
    return general_message_list
