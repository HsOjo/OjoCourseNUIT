from saika import Config, common
from saika.decorator import *

from app import redis
from app.api.info.service import InfoService
from app.api.user.decorator import ignore_auth
from app.api.user.user_api import UserAPIController
from app.config.nuit import NUITConfig
from app.libs.nuit import NUIT
from app.libs.nuit.nuit import AccessError
from .enums import *

RK_COOKIES = 'cookies'


@doc('信息模块')
@controller
class Info(UserAPIController):
    def callback_before_register(self):
        super().callback_before_register()

        @self.blueprint.errorhandler(AccessError)
        def refresh_cookies(e):
            redis.cli.delete(RK_COOKIES)
            self.error(*ACCESS_ERROR)

    @property
    def nuit(self):
        cfg = Config.get(NUITConfig)  # type: NUITConfig

        cookies_str = redis.cli.get(RK_COOKIES)
        if cookies_str:
            cookies = common.from_json(cookies_str)
        else:
            cookies = NUIT(cfg.url_base).login(**cfg.account)
            cookies_str = common.to_json(cookies, ensure_ascii=False)
            redis.cli.set(RK_COOKIES, cookies_str)

        return NUIT(cfg.url_base, cookies)

    @property
    def service(self):
        return InfoService(self.nuit)

    @doc('学院信息')
    @ignore_auth
    @get
    @rule('/colleges')
    def colleges(self):
        self.success(**self.service.college_info())

    @doc('专业信息')
    @ignore_auth
    @get
    @rule('/majors/<string:college>')
    def majors(self, college: str):
        self.success(**self.service.major_info(college))

    @doc('班级信息')
    @ignore_auth
    @get
    @rule('/classes/<string:college>/<string:major>/<int:grade>')
    def classes(self, college: str, major: str, grade: int):
        self.success(**self.service.class_info(college, major, grade))

    @doc('课程信息')
    @get
    @rule('/courses')
    def courses(self):
        info = self.current_user.info
        self.success(**self.service.course_info(info.class_))

    @doc('学期信息')
    @get
    @rule('/semester')
    def semester(self):
        self.success(**self.service.semester_info())
