import datetime
import hashlib

from saika import db, common, Service, Config

from app.config import UserConfig
from app.models.user import User, UserInfo


class UserExistedError(Exception):
    pass


class UserService(Service):
    def __init__(self):
        super().__init__(User)

    @staticmethod
    def pw_hash(x: str):
        return hashlib.md5(x.encode()).hexdigest()

    def register(self, username, password, nickname, stu_num, college, major, grade, class_):
        if self.query.filter_by(username=username).first():
            raise UserExistedError

        password = self.pw_hash(password)
        return super().add(
            username=username, password=password,
            info=UserInfo(
                nickname=nickname,
                stu_num=stu_num,
                college=college,
                major=major,
                grade=grade,
                class_=class_,
            )
        )

    def login(self, username, password):
        password = self.pw_hash(password)
        item = self.query.filter_by(
            username=username,
            password=password,
        ).first()  # type: User

        if item is None:
            return False
        else:
            cfg = Config.get(UserConfig)  # type: UserConfig
            login_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            return common.obj_encrypt(dict(
                id=item.id, time=login_time,
            ), cfg.login_expires)

    def change_password(self, username, old, new):
        password = self.pw_hash(old)
        item = self.query.filter_by(
            username=username,
            password=password,
        ).first()  # type: User

        if item is None:
            return False
        else:
            item.password = self.pw_hash(new)
            db.add_instance(item)
            return True

    def get_user(self, token: str):
        obj = common.obj_decrypt(token)  # type: dict
        if obj is not None:
            id = obj.get('id')
            time = datetime.datetime.strptime(obj.get('time'), '%Y-%m-%d %H:%M:%S')
            if id is not None:
                item = self.query.get(id)  # type: User
                if item is not None:
                    if not item.update_time or (time - item.update_time).total_seconds() > 0:
                        return item

        return None
