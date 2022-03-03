import redis
from flask_redis import FlaskRedis
from redis_lock import Lock
from saika import common


class Redis(FlaskRedis):
    @property
    def cli(self):
        cli = self._redis_client  # type: redis.Redis
        return cli

    def lock(self, name, expire=None, **kwargs):
        return Lock(self.cli, name, expire, **kwargs)

    def set(self, key, obj, expire=None, **kwargs):
        kwargs.setdefault('ex', expire)
        obj = common.obj_standard(obj, str_key=True, str_obj=True, str_type=True)
        obj = common.to_json(obj)
        self.cli.set(key, obj, **kwargs)

    def get(self, key, default=None):
        if not self.cli.exists(key):
            return default

        obj_data = self.cli.get(key)  # type: bytes
        if not obj_data:
            return default

        obj_str = obj_data.decode()
        return common.from_json(obj_str)
