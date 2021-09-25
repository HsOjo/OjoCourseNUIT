from app import cache
from app.libs.nuit import NUIT

CK_BASIC_INFO = 'info:basic'
CK_MAJOR_INFO = 'info:major'
CK_CLASS_INFO = 'info:class'
CK_COURSE_INFO = 'info:course'
CK_DATE_INFO = 'info:date'


class InfoService:
    def __init__(self, nuit):
        self._nuit = nuit  # type: NUIT

    def basic_info(self):
        return self._nuit.get_basic_info()

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
        result = self._nuit.get_major_info(college)
        return result

    def class_info(self, college, major, grade):
        result = self._nuit.get_class_info(college, major, grade)
        return result

    def course_info(self, class_, week=''):
        basic_info = self.basic_info()
        stu_year = basic_info['stu_year']
        result = self._nuit.get_course_info(class_, stu_year, week)
        return result

    def date_info(self, stu_year):
        basic_info = self.basic_info()
        result = self._nuit.get_date_info(stu_year, basic_info['week_total'])
        return result
