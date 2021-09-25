from saika import BaseConfig
from saika.decorator import config
from sqlalchemy.engine import make_url, URL


@config
class RedisConfig(BaseConfig):
    host = '127.0.0.1'
    port = 6379
    password = ''
    query_args = dict(
        db=0,
    )

    def merge(self) -> dict:
        url = make_url('redis://:%(password)s@%(host)s:%(port)d' % self.data)  # type: URL
        url.update_query_pairs([
            (k, str(v)) for k, v in self.query_args.items()
        ])
        return dict(
            REDIS_URL=str(url),
            CACHE_TYPE='redis',
            CACHE_REDIS_URL=str(url),
        )
