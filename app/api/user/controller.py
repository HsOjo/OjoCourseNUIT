from saika import db
from saika.decorator import *

from app.models.user import User as Model
from .decorator import ignore_auth
from .enums import *
from .forms import *
from .service import UserExistedError
from .user_api import UserAPIController
from ..enums import EDIT_SUCCESS


@doc('用户模块')
@controller
class User(UserAPIController):
    @doc('用户注册')
    @ignore_auth
    @post
    @rule('/register')
    @form(RegisterForm)
    def register_(self):
        data = self.form.data.copy()
        try:
            self.service_user.register(**data)
        except UserExistedError:
            self.error(*REGISTER_FAILED)
        else:
            self.success(*REGISTER_SUCCESS)

    @doc('用户登录')
    @ignore_auth
    @post
    @rule('/login')
    @form(LoginForm)
    def login(self):
        data = self.form.data.copy()

        token = self.service_user.login(**data)
        if not token:
            self.error(*LOGIN_FAILED)

        self.success(*LOGIN_SUCCESS, token=token)

    @doc('用户信息')
    @get
    @rule('/info')
    def info(self):
        self.success(
            **db.dump_instance(self.current_user, '*', lambda user: dict(
                **db.dump_instance(user.info, hidden_columns=['*_id']),
            ), hidden_columns=[Model.password, '*_time']))

    @doc('用户信息编辑')
    @form(InfoEditForm)
    @post
    @rule('/info-edit')
    def info_edit(self):
        user_info = self.current_user.info
        for k, v in self.form.data.items():
            setattr(user_info, k, v)
        db.add_instance(user_info)
        self.success(*EDIT_SUCCESS)

    @doc('用户修改密码')
    @form(ChangePasswordForm)
    @post
    @rule('/change-password')
    def change_password(self):
        result = self.service_user.change_password(self.current_user.username, **self.form.data)
        if not result:
            self.error(*CHANGE_PASSWORD_FAILED)

        self.success(*CHANGE_PASSWORD_SUCCESS)
