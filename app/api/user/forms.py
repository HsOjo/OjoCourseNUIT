from saika.form import JSONForm
from wtforms import StringField
from wtforms.validators import DataRequired


class LoginForm(JSONForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = StringField('密码', validators=[DataRequired()])


class RegisterForm(LoginForm):
    nickname = StringField('姓名', validators=[DataRequired()])
    stu_num = StringField('学号', validators=[DataRequired()])
    college = StringField('院系', validators=[DataRequired()])
    major = StringField('专业', validators=[DataRequired()])
    grade = StringField('年级', validators=[DataRequired()])
    class_ = StringField('班级', validators=[DataRequired()])


class ChangePasswordForm(JSONForm):
    old = StringField('旧密码', validators=[DataRequired()])
    new = StringField('新密码', validators=[DataRequired()])


class InfoEditForm(JSONForm):
    stu_num = StringField('学号', validators=[DataRequired()])
    college = StringField('院系', validators=[DataRequired()])
    major = StringField('专业', validators=[DataRequired()])
    grade = StringField('年级', validators=[DataRequired()])
    class_ = StringField('班级', validators=[DataRequired()])
    password = StringField('教务系统密码')
