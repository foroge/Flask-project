from datetime import datetime
import os
import sys
import json

from flask import Flask, render_template, redirect, Response, request, make_response, jsonify, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from sqlalchemy.sql.expression import func

from forms.user import RegisterForm, LoginForm
from forms.card import CardForm
from forms.game_characteristic import StartGameForm

from data.user import User
from data.cards import Card
from data import db_session

from forms.user_func import save_user, load_user_form
from forms.card_func import save, load_random_card, name_change, save_card, reload_card, load_card

from extra_utilities import get_duration


PATH = "\\".join(sys.argv[0].split("\\")[:-2])

path_templates = os.path.join(PATH, "templates")
path_static = os.path.join(PATH, "data")
app = Flask(__name__, template_folder=path_templates, static_folder=path_static)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/game', methods=["GET", 'POST'])
def game():
    db_sess = db_session.create_session()

    title = "Try to guess the card"

    if request.method == "POST":
        title = "You guessed wrong"

        data = request.json
        card = db_sess.get(Card, data["card_id"])
        title_card = card.title
        user = db_sess.get(User, current_user.get_id())
        if data["answer"] == title_card:
            if "increasing" in data["text"]:
                card.rating += 0.1
            elif "reduction" in data["text"]:
                card.rating -= 0.1
            user.rating_user += 0.1
            title = "You guessed!"
        else:
            user.rating_user -= 0.1

        db_sess.commit()
        db_sess.close()

    card = load_random_card()
    found_card = "No cards found"
    if card:
        found_card = "Cards found!"
        return render_template("game.html", data=card, found_card=found_card, title=title)
    return render_template("game.html", found_card=found_card, title=title)


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
def load_user(user_id: int) -> User:
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
        return redirect(f"/game/{form.question.data}")
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


@app.route('/rating/<sort>', methods=['GET', 'POST'])
def rating(sort='rating_whole'):
    db_sess = db_session.create_session()
    users: list
    if sort == 'rating_cards':
        users = db_sess.query(User).order_by(User.rating_cards.desc()).limit(10).all()
        rating = 'rating_cards'
    elif sort == 'rating_user':
        users = db_sess.query(User).order_by(User.rating_user.desc()).limit(10).all()
        rating = 'rating_user'
    else:
        users = db_sess.query(User).order_by(User.rating_whole.desc()).limit(10).all()
        rating: str = 'rating_whole'
    for user in users:
        user.update()
    users = [dict(login=user.login, rating=round(getattr(user, rating), 2)) for user in users]
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
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()
