from datetime import datetime

from saika import db


class Course(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    user_id = db.Column(db.INTEGER, db.ForeignKey('user.id'), index=True)
    data = db.Column(db.JSON)
    update_time = db.Column(db.DATETIME, onupdate=datetime.now)
