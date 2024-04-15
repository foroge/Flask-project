import sys

from flask import render_template, url_for, redirect, Response

from data.user import User

sys.path.append("\\".join(sys.argv[0].split("\\")[:-1]))
from .user import RegisterForm, LoginForm


def register_form_check(form: RegisterForm, mode: str, user_id: int) -> str | None:
    title = "Register" if mode == "register" else "Change user"
    age = form.age.data
    if type(age) is not int:
        return render_template('register.html', title=title,
                               form=form,
                               message="Age is not integer")
    elif not (0 <= age <= 130):
        return render_template('register.html', title=title,
                               form=form,
                               message="Age is not real")
    elif form.password.data != form.password_again.data:
        return render_template('register.html', title=title,
                               form=form,
                               message="Passwords do not match")
    from main import db_session
    db_sess = db_session.create_session()
    if mode == "register":
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title=title,
                                   form=form,
                                   message="Such a user already exists")
    if mode == "edit":
        if not db_sess.get(User, user_id):
            return render_template('register.html', title=title,
                                   form=form,
                                   message="User is not found")
    db_sess.close()


def save_user(form: RegisterForm, mode="register", user_id=None) -> Response:
    check = register_form_check(form, mode, user_id)
    if check:
        return check

    from main import db_session

    db_sess = db_session.create_session()

    print(user_id, db_sess.get(User, user_id))

    user = User() if mode == "register" else db_sess.get(User, user_id)
    user.email = form.email.data
    user.set_password(form.password.data)
    user.login = form.login.data
    user.age = form.age.data

    db_sess.add(user) if mode == "register" else ...
    db_sess.commit()
    db_sess.close()
    return redirect('/login')


def load_user_form(form: RegisterForm, user_id: int) -> str:
    from main import db_session
    from main import current_user

    db_sess = db_session.create_session()
    cur_user_id = int(current_user.get_id())
    if cur_user_id == 1 or cur_user_id == user_id:
        user = db_sess.get(User, user_id)
        form.email.data = user.email
        form.login.data = user.login
        form.age.data = user.age
        return render_template('register.html', title='Change user', form=form)
    return render_template('base.html', title=title, message="You have no rights")
