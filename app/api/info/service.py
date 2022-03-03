from saika import Service, Config

from app import redis
from app.config import NUITConfig
from app.libs.nuit import NUIT, AccessError
from app.models.course import Course
from app.models.user import User

RK_COOKIES = 'cookies'


class CourseService(Service):
    def __init__(self):
        super().__init__(Course)

    @property
    def service_info(self):
        return InfoService()

    def get_info(self, user: User):
        info = self.service_info.course_info(user.info.class_)
        if info:
            self.filters(user_id=user.id).without_pk_filter.edit(data=info)
        else:
            course = self.filters(user_id=user.id).get_one()  # type: Course
            info = course.data

        return info


class InfoService:
    @property
    def nuit(self):
        cfg = Config.get(NUITConfig)  # type: NUITConfig

        cookies = redis.get(RK_COOKIES)
        if cookies is None:
            cookies = NUIT(cfg.url_base).login(**cfg.account)
            redis.set(RK_COOKIES, cookies)

        return NUIT(cfg.url_base, cookies)

    def basic_info(self):
        return self.nuit.get_basic_info()

    def college_info(self):
        result = self.basic_info()
        colleges = {k: v for k, v in result.pop('colleges').items() if v}
        grades = {k: v for k, v in result.pop('grades').items() if v}
        return dict(
            colleges=colleges,
            grades=grades,
        )

    def semester_info(self):
        result = self.basic_info()
        result.pop('colleges')
        result['dates'] = self.date_info(result.get('stu_year'))
        return result

    def major_info(self, college):
        result = self.nuit.get_major_info(college)
        return result

    def class_info(self, college, major, grade):
        result = self.nuit.get_class_info(college, major, grade)
        return result

    def course_info(self, class_, week=''):
        try:
            basic_info = self.basic_info()
            stu_year = basic_info['stu_year']
            result = self.nuit.get_course_info(class_, stu_year, week)
        except AccessError:
            redis.cli.delete(RK_COOKIES)
            result = None

        return result

    def date_info(self, stu_year):
        basic_info = self.basic_info()
        result = self.nuit.get_date_info(stu_year, basic_info['week_total'])
        return result
