import base64
import json
import re
from datetime import datetime, timedelta

import bs4
import requests
from bs4 import Tag
from requests import Response


class AccessError(Exception):
    pass


class NUIT:
    def __init__(self, url_base, cookies=None):
        self._cookies = cookies
        self._url_base = url_base

    def request(self, method, path, **kwargs):
        kwargs.setdefault('url', self._url_base + path)
        kwargs.setdefault('cookies', self._cookies)
        resp = getattr(requests, method)(**kwargs)  # type: Response
        if 'login_form' in resp.text or resp.status_code != 200:
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
        [week_total] = re.findall(r'\$zc\.val\((\d+)\);//ζεδΈε¨', resp.text)
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
            xnxqdm=stu_year,  # ε­¦εΉ΄ε­¦ζδ»£η 
            rxnf=grade,  # ε₯ε­¦εΉ΄δ»½
            xsyxdm=college,  # ε­¦ηι’η³»δ»£η 
            zydm=major,  # δΈδΈδ»£η 
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
                id=int(course['kcdm']),  # θ―Ύη¨δ»£η 
                num=course['kcbh'],  # θ―Ύη¨ηΌε·
                name=course['kcmc'],  # θ―Ύη¨εη§°
                class_name=course['jxbmc'],  # η­ηΊ§εη§°
                student_num=int(course['pkrs']),  # ζθ―ΎδΊΊζ°
                teacher=course['teaxms'],  # ζεΈ
                week=int(course['zc']),  # ε¨ζ¬‘
                day=int(course['xq']),  # ζζ
                node_nums=course['jcdm2'].split(','),  # θζ¬‘
                place=course['jxcdmc'],  # δΈθ―Ύε°ηΉ
                type=course['jxhjmc'],  # η±»ε
                time=int(course['xs']),  # ε­¦ζΆ
                total_time=int(course['zxs']),  # ζ»ε­¦ζΆ
                introduction=course['sknrjj'],  # δΈθ―Ύεε?Ήη?δ»
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
