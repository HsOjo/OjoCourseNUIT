from saika import BaseConfig
from saika.decorator import config


@config
class NUITConfig(BaseConfig):
    url_base = 'http://[host]'
    account = dict(username='[username]', password='[password]')
