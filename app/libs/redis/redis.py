import redis
from flask_redis import FlaskRedis
from redis_lock import Lock


class Redis(FlaskRedis):
    @property
    def cli(self):
        cli = self._redis_client  # type: redis.Redis
        return cli

    def lock(self, name, expire=None, **kwargs):
        return Lock(self.cli, name, expire, **kwargs)
