import base64
import json
import re
from datetime import datetime, timedelta

import bs4
import requests
from bs4 import Tag


class AccessError(Exception):
    pass


class NUIT:
    def __init__(self, url_base, cookies=None):
        self._cookies = cookies
        self._url_base = url_base

    def request(self, method, path, **kwargs):
        kwargs.setdefault('url', self._url_base + path)
        kwargs.setdefault('cookies', self._cookies)
        resp = getattr(requests, method)(**kwargs)
        if 'login_form' in resp.text:
            raise AccessError
        return resp

    def set_cookies(self, cookies):
        self._cookies = cookies

    def login(self, username, password: str):
        password = base64.b64encode(password.encode()).decode()

        sess = requests.session()
        sess.get(self._url_base)
        sess.post(self._url_base + '/login!doLogin.action', data=dict(
            account=username,
            pwd=password,
            verifycode='',
        ))

        return sess.cookies.get_dict()

    def get_basic_info(self):
        resp = self.request('get', '/xsbjkbcx!xsbjkbMain.action')
        bs = bs4.BeautifulSoup(resp.text, 'html.parser')

        stu_year_option = bs.select_one('#xnxqdm option[selected]')
        college_select = bs.select_one('#xsyxdm')
        grade_select = bs.select_one('#rxnf')

        [week_current] = re.findall(r'var val = .+?(\d+).+', resp.text)
        [week_total] = re.findall(r'\$zc\.val\((\d+)\);//最后一周', resp.text)
        stu_year = stu_year_option.attrs.get('value')
        colleges = {tag.text: tag.attrs.get('value') for tag in college_select.children}
        grades = {tag.text: tag.attrs.get('value') for tag in grade_select.children}

        return dict(
            week_current=int(week_current),
            week_total=int(week_total),
            stu_year=stu_year,
            colleges=colleges,
            grades=grades,
        )

    def get_mixed_info(self, guid, college='', major='', grade='', stu_year=''):
        resp = self.request('post', '/xsbjkbcx!getFind.action', data=dict(
            guid=guid,
            xnxqdm=stu_year,  # 学年学期代码
            rxnf=grade,  # 入学年份
            xsyxdm=college,  # 学生院系代码
            zydm=major,  # 专业代码
        ))

        data = None
        match = re.match(r'^%s\^getFind:(?P<data>.+)$' % guid, resp.text)
        if match:
            data = match.groupdict()['data']
            data = json.loads(data)
            data = {i['mc']: i['dm'] for i in data}

        return data

    def get_major_info(self, college):
        return self.get_mixed_info('xsyxdm', college)

    def get_class_info(self, college, major, grade=''):
        return self.get_mixed_info('zydm', college, major, grade)

    def get_course_info(self, class_, stu_year, week=''):
        resp = self.request('get', '/xsbjkbcx!getKbRq.action', params=dict(
            bjdm=class_,
            xnxqdm=stu_year,
            zc=week,
        ))

        [courses, dates] = resp.json()

        courses_tmp = [
            dict(
                id=int(course['kcdm']),  # 课程代码
                num=course['kcbh'],  # 课程编号
                name=course['kcmc'],  # 课程名称
                class_name=course['jxbmc'],  # 班级名称
                student_num=int(course['pkrs']),  # 排课人数
                teacher=course['teaxms'],  # 教师
                week=int(course['zc']),  # 周次
                day=int(course['xq']),  # 星期
                node_nums=course['jcdm2'].split(','),  # 节次
                place=course['jxcdmc'],  # 上课地点
                type=course['jxhjmc'],  # 类型
                time=int(course['xs']),  # 学时
                total_time=int(course['zxs']),  # 总学时
                introduction=course['sknrjj'],  # 上课内容简介
            ) for course in courses
        ]

        courses = []
        for course in courses_tmp:
            for node_num in course.pop('node_nums'):
                node_num = int(node_num)
                courses.append(dict(
                    node_num=node_num, **course,
                ))

        dates = {date['xqmc']: date['rq'] for date in dates}

        return dict(
            courses=courses,
            dates=dates,
        )

    def get_date_info(self, stu_year, total_week=None):
        resp = self.request('get', '/xlxx!getXlxx.action', params=dict(
            xnxqdm=stu_year
        ))

        bs = bs4.BeautifulSoup(resp.text, 'html.parser')
        week_tags = bs.select('tr td:first-child')

        last_week = 0
        week_dates = {}
        for week_tag in week_tags:
            week_tag: Tag
            last_week = week = int(week_tag.text)

            row_tag = week_tag.parent  # type: Tag
            month_tag = row_tag.select_one('.month')  # type: Tag
            day_tags = row_tag.select('.day')

            days = week_dates.get(week, [])
            if not days:
                week_dates[week] = days

            for day_tag in day_tags:
                date = '%s-%02d' % (month_tag.text, int(day_tag.text))
                days.append(date)

        if total_week is not None and last_week < total_week:
            last_day = None
            for week in range(last_week, total_week + 1):
                days = week_dates.get(week, [])

                if not days:
                    week_dates[week] = days
                else:
                    last_day = datetime.strptime(days[-1], '%Y-%m-%d')

                for _ in range(7 - len(days)):
                    last_day += timedelta(days=1)
                    days.append(last_day.strftime('%Y-%m-%d'))

        return week_dates
