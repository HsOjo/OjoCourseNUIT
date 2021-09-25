from saika import MetaTable, APIController
from saika.context import Context

from app.models.user import User
from .enums import *

GK_USER = 'user'
HK_AUTH = 'Authorization'
MK_PUBLIC = 'public'
MK_ROLES = 'roles'


class UserAPIController(APIController):
    @property
    def service_user(self):
        from .service import UserService
        return UserService()

    def callback_before_register(self):
        super().callback_before_register()

        @self.blueprint.before_request
        def authentication():
            if self.request.method == 'OPTIONS':
                return ''

            f = Context.get_view_function()
            if f is None or MetaTable.get(f, MK_PUBLIC):
                return

            token = self.request.headers.get(HK_AUTH)
            user = self.service_user.get_user(token)
            if user is None:
                self.error(*TOKEN_INVALID)

            self.context.g_set(GK_USER, user)

    @property
    def current_user(self):
        user = self.context.g_get(GK_USER)  # type: User
        return user
