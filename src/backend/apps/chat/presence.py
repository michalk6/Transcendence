from redis import asyncio
from django.conf import settings


PRESENCE_TTL = 60
redis_client = asyncio.from_url(settings.REDIS_URL)


def presence_key(user_id):
    return f"presence:user:{user_id}"


async def add_connection(user_id, channel_name):
    key = presence_key(user_id)
    await redis_client.sadd(key, channel_name)
    await redis_client.expire(key, PRESENCE_TTL)
    
    
async def refresh_presence(user_id):
    key = presence_key(user_id)
    await redis_client.expire(key, PRESENCE_TTL)


async def remove_connection(user_id, channel_name):
    key = presence_key(user_id)
    await redis_client.srem(key, channel_name)


async def get_online_user_ids():
    async_iter = redis_client.scan_iter(presence_key("*"))
    users = set()
    async for key in async_iter:
        user_id = int(key.decode("utf-8").split(":")[-1])
        users.add(user_id)
    return users


async def is_online(user_id):
    return await redis_client.scard(presence_key(user_id)) > 0
