import datetime
import sqlalchemy
from data.db_session import SqlAlchemyBase
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin


class Card(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'cards'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    promt = sqlalchemy.Column(sqlalchemy.String)
    rating = sqlalchemy.Column(sqlalchemy.Float)
    create_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')
