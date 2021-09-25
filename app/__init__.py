from flask_caching import Cache
from saika import SaikaApp

from app.libs.redis import Redis


class Application(SaikaApp):
    def callback_init_app(self):
        self.set_form_validate_default(True)
        redis.init_app(self)
        cache.init_app(self)


redis = Redis()
cache = Cache()
app = Application()
