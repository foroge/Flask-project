import datetime
import sqlalchemy

from data.db_session import SqlAlchemyBase
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin

from .cards import ComplitedCard


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    login = sqlalchemy.Column(sqlalchemy.String)
    age = sqlalchemy.Column(sqlalchemy.Integer)
    rating_user = sqlalchemy.Column(sqlalchemy.Float, default=10)
    rating_whole = sqlalchemy.Column(sqlalchemy.Float, default=0)
    rating_cards = sqlalchemy.Column(sqlalchemy.Float, default=0)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String)
    create_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())

    cards = orm.relationship("Card", back_populates='user')

    complited_cards = orm.relationship('Card', secondary=ComplitedCard, back_populates='user',
                                       overlaps="finished_users")

    def set_password(self, password: str) -> None:
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.hashed_password, password)

    def update(self) -> None:
        self.rating_cards = round(sum([card.rating for card in self.cards]), 2)
        if self.cards:
            self.rating_whole = round(sum([card.rating for card in self.cards]) + self.rating_user, 3)
        else:
            self.rating_whole = self.rating_user
