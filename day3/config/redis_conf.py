import json
from typing import Any

import redis.asyncio as redis

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True
)

# 设置读取方法
# 1.字符串读取
async def get_cache_str(key: str):
    try:
        return await redis_client.get(key)
    except Exception as e:
        print(f"读取redis数据失败:{e}")
        return  None

# 2.列表读取
async def get_cache_list(key: str):
    try:
        data = await redis_client.get(key)
        if data:
            # 反序列化数据
            return json.loads(data)
    except Exception as e:
        print(f"读取redis数据失败:{e}")
        return  None

#写入数据
async def set_cache(key: str, value: Any, expire: int = 600):
    try:
        if isinstance(value, (dict, list)):
            # 序列化数据
            value = json.dumps(value, ensure_ascii=False)
        await redis_client.set(key, value, ex=expire)
        return True
    except Exception as e:
        print(f"写入redis数据失败:{e}")
        return  False