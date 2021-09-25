from saika.database.config import ConnectDBConfig
from saika.decorator import config


@config
class DatabaseConfig(ConnectDBConfig):
    driver = 'mysql+pymysql'
    query_args = dict(
        charset='utf8mb4'
    )
