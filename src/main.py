import os
import sys

from flask import Flask, render_template, redirect, request, make_response, jsonify, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename

from forms.user import RegisterForm, LoginForm
from forms.card import CardForm

from data.user import User
from data.cards import Card
from data import db_session

from extra_utilities import json_save, save, name_change, save_card, reload_card


PATH = "\\".join(sys.argv[0].split("\\")[:-2])

path_templates = os.path.join(PATH, "templates", )
app = Flask(__name__, template_folder=path_templates, static_folder="data")
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/edit_card/<int:card_id>', methods=["GET", 'POST'])
def edit_card(card_id):
    form = CardForm()

    if request.method == "GET":
        db_sess = db_session.create_session()

        card = db_sess.get(Card, card_id)
        form.title.data = card.title
        form.promt.data = card.promt

    if form.validate_on_submit():
        db_sess = db_session.create_session()

        card = Card()
        card.user = current_user
        card.title = form.title.data
        card.promt = form.promt.data

        path = os.path.join(PATH, f"cards/card_{card.id}")
        for i, image in enumerate(form.images.data):
            path_save = os.path.join(path, f"card_{i}")
            image.save(path_save)

        db_sess.add(card)
        db_sess.commit()
        db_sess.close()


@app.route('/create_card', methods=["GET", 'POST'])
def create_card():
    form = CardForm()

    if form.is_submitted() and not form.submit_btn.data:
        return reload_card(form, 'card_form.html', title='Карточка')
    elif form.validate_on_submit():
        return save_card(form)
    return render_template('card_form.html', title='Карточка', form=form)


@login_manager.user_loader
def load_user(user_id):
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
    return render_template('base.html', title='Индекс')


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
        try:
            age = int(form.age.data)
        except ValueError:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Возраст не является числом")
        if not (0 <= age <= 130):
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Возраст не является реальным")
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User()
        user.email = form.email.data
        user.set_password(form.password.data)
        user.login = form.login.data
        user.age = form.age.data

        db_sess.add(user)
        db_sess.commit()
        db_sess.close()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


def main():
    path_db = os.path.join(PATH, "db/user.db")
    db_session.global_init(path_db)
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()
