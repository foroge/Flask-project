from datetime import datetime
import os
import sys
import json

from flask import Flask, render_template, redirect, Response, request, make_response, jsonify, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import reqparse, abort, Api, Resource

from werkzeug.utils import secure_filename
from sqlalchemy.sql.expression import func

from forms.user import RegisterForm, LoginForm
from forms.card import CardForm
from forms.game import GameForm
from forms.game_characteristic import StartGameForm
from forms.answer_sumbit import AnswerForm

from data.user import User
from data.cards import Card
from data import db_session, user_resources

from forms.user_func import save_user, load_user_form
from forms.card_func import save, load_random_card, name_change, save_card, reload_card, load_card
from forms.game_func import load_game, reload_game

from extra_utilities import get_duration

PATH = "\\".join(sys.argv[0].split("\\")[:-2])

path_templates = os.path.join(PATH, "templates")

from data import user_api

path_static = os.path.join(PATH, "data")

app = Flask(__name__, template_folder=path_templates, static_folder=path_static)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@app.errorhandler(404)
def not_found(_):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


@app.route('/answer/<string:title>', methods=["GET", 'POST'])
def answer(title):
    form = AnswerForm()
    if request.method == "GET":
        title = f"The correct answer is '{title}'" if title != "False" else "You guessed"
        return render_template("answer.html", title=title, form=form)
    if form.validate_on_submit():
        return redirect("/game")


@app.route('/game', methods=["GET", 'POST'])
def game():
    form = GameForm()
    if request.method == "GET":
        return load_game(form)
    if form.is_submitted():
        return reload_game(form)
    return load_game(form)


@app.route('/delete_card/<int:card_id>', methods=["GET", 'POST'])
def delete_card(card_id: int) -> Response:
    db_sess = db_session.create_session()

    cur_user_id: int = int(current_user.get_id())

    card = (db_sess.query(Card).filter(Card.id == card_id)
            .filter(Card.user_id == cur_user_id | cur_user_id == 1).first())

    if card:
        db_sess.delete(card)
        db_sess.commit()
    else:
        abort(404)

    return redirect('/')


@app.route('/edit_card/<int:card_id>', methods=["GET", 'POST'])
def edit_card(card_id: int) -> Response | str:
    form = CardForm()
    if request.method == "GET":
        return load_card(form=form, name='card_form.html', title='Карточка', card_id=card_id)
    if form.is_submitted() and not form.submit_btn.data:
        return reload_card(form=form, name='card_form.html', title='Карточка')
    elif form.validate_on_submit():
        return save_card(form, mode="edit", card_id=card_id)


@app.route('/create_card', methods=["GET", 'POST'])
def create_card() -> Response | str:
    form = CardForm()
    if form.is_submitted() and not form.submit_btn.data:
        return reload_card(form, 'card_form.html', title='Карточка')
    elif form.validate_on_submit():
        return save_card(form, mode="create")
    return render_template('card_form.html', form=form, title='Карточка')


@login_manager.user_loader
def load_user(user_id: int):
    db_sess = db_session.create_session()
    user = db_sess.get(User, user_id)
    db_sess.close()
    return user


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = StartGameForm()
    if form.is_submitted():
        return redirect(f"/game")
    return render_template("index.html", form=form)


@app.route('/user_data')
def user_data() -> str:
    db_sess = db_session.create_session()

    user = db_sess.get(User, int(current_user.get_id()))
    user.update()

    user_dict = user.__dict__
    cards: list = user.cards

    date = user.create_date
    cur_date = datetime.now()
    user_dict["create_date"] = get_duration(date, cur_date)

    db_sess.close()

    return render_template("user_data.html", user=user_dict, cards=cards)


@app.route('/rating', methods=['GET', 'POST'])
@app.route('/rating/<sort>', methods=['GET', 'POST'])
def rating(sort='rating_whole'):
    db_sess = db_session.create_session()
    users: list
    if sort == 'rating_cards':
        users = db_sess.query(User).order_by(User.rating_cards.desc()).limit(10).all()
        rating_name = 'rating_cards'
    elif sort == 'rating_user':
        users = db_sess.query(User).order_by(User.rating_user.desc()).limit(10).all()
        rating_name = 'rating_user'
    else:
        users = db_sess.query(User).order_by(User.rating_whole.desc()).limit(10).all()
        rating_name: str = 'rating_whole'
    for user in users:
        user.update()
        db_sess.commit()
    users = [dict(login=user.login, rating=round(getattr(user, rating_name), 2)) for user in users]
    db_sess.close()
    return render_template('rating.html', top_users=users)


@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id: int) -> str | Response:
    form = RegisterForm()

    if request.method == "GET":
        load_user_form(form, user_id)

    if form.validate_on_submit():
        return save_user(form, mode="edit", user_id=user_id)
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        return save_user(form)
    return render_template('register.html', title='Регистрация', form=form)


def main():
    path_db = os.path.join(PATH, "db/user.db")
    db_session.global_init(path_db)

    app.register_blueprint(user_api.blueprint)

    api.add_resource(user_resources.UserListResource, '/api_restful/users')
    api.add_resource(user_resources.UserResource, '/api_restful/users/<int:users_id>')

    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()
