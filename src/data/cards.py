import datetime
import sqlalchemy
from data.db_session import SqlAlchemyBase
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

ComplitedCard = sqlalchemy.Table('ComplitedCard',
                                 SqlAlchemyBase.metadata,
                                 sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
                                 sqlalchemy.Column('finished_user_id', sqlalchemy.Integer,
                                                   sqlalchemy.ForeignKey('cards.id')),
                                 sqlalchemy.Column('complited_card_id', sqlalchemy.Integer,
                                                   sqlalchemy.ForeignKey('users.id'))
                                 )


class Card(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'cards'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    promt = sqlalchemy.Column(sqlalchemy.String)
    rating = sqlalchemy.Column(sqlalchemy.Float, default=0)
    create_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User', foreign_keys=[user_id])

    finished_users = orm.relationship("User", secondary=ComplitedCard)


class CurrentCard(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'current_card'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    card_id = sqlalchemy.Column(sqlalchemy.Integer)
    user_id = sqlalchemy.Column(sqlalchemy.Integer)