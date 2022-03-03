from saika.decorator import *

from app.api.user.decorator import ignore_auth
from app.api.user.user_api import UserAPIController
from app.libs.nuit import AccessError
from .enums import *


@doc('信息模块')
@controller
class Info(UserAPIController):
    def callback_before_register(self):
        super().callback_before_register()

        @self.blueprint.errorhandler(AccessError)
        def refresh_cookies(e):
            return self.response(*ACCESS_ERROR)

    @property
    def service(self):
        from .service import InfoService
        return InfoService()

    @property
    def service_course(self):
        from .service import CourseService
        return CourseService()

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
        info = self.service_course.get_info(self.current_user)
        if info is None:
            self.error(*OTHER_TIME_ERROR)
        self.success(*INFO_SUCCESS, **info)

    @doc('学期信息')
    @get
    @rule('/semester')
    def semester(self):
        self.success(**self.service.semester_info())
