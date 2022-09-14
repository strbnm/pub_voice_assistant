from app.settings.config import settings
from redis import StrictRedis

redis_connection = StrictRedis(
    host=settings.REDIS.HOST, port=settings.REDIS.PORT, decode_responses=True
)
