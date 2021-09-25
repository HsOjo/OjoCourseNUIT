from datetime import datetime

from saika import db
from saika.decorator import model


@model
class User(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    username = db.Column(db.VARCHAR(191), unique=True)
    password = db.Column(db.VARCHAR(255))
    create_time = db.Column(db.DATETIME, default=datetime.now)
    update_time = db.Column(db.DATETIME, onupdate=datetime.now)

    info = db.relationship('UserInfo', uselist=False)  # type: UserInfo


@model
class UserInfo(db.Model):
    user_id = db.Column(db.INTEGER, db.ForeignKey(User.id), primary_key=True, index=True)
    nickname = db.Column(db.VARCHAR(191), index=True)
    stu_num = db.Column(db.VARCHAR(191), index=True)
    college = db.Column(db.VARCHAR(191), index=True)
    major = db.Column(db.VARCHAR(191), index=True)
    grade = db.Column(db.VARCHAR(191), index=True)
    class_ = db.Column(db.VARCHAR(191), index=True)
    password = db.Column(db.VARCHAR(191))
