import os
import json
import sys
import shutil
from datetime import datetime, timedelta

import flask
from flask import render_template, url_for, redirect, Response
from flask_wtf import FlaskForm

from data.cards import Card
from data.user import User


def get_duration(then: datetime, now=datetime.now()) -> str:

    duration = now - then
    duration_in_s = duration.total_seconds()

    def years() -> tuple[float, float]:
        return divmod(duration_in_s, 31536000)

    def days(sec=0) -> tuple[float, float]:
        return divmod(sec if sec else duration_in_s, 86400)

    def hours(sec=0) -> tuple[float, float]:
        return divmod(sec if sec else duration_in_s, 3600)

    def minutes(sec=0) -> tuple[float, float]:
        return divmod(sec if sec else duration_in_s, 60)

    def seconds(sec=0) -> tuple[float, float]:
        return divmod(sec if sec else duration_in_s, 1)

    def total_duration() -> str:
        y: tuple = years()
        d: tuple = days(y[1])
        h: tuple = hours(d[1])
        m: tuple = minutes(h[1])
        s: tuple = seconds(m[1])

        return (f"{int(y[0])} years, {int(d[0])} days, {int(h[0])} hours, "
                f"{int(m[0])} minutes and {int(s[0])} seconds")
    return total_duration()


def name_change(data: list, name: str):
    for i, file in enumerate(data):
        file.name = f"{name}_{i}{os.path.splitext(os.path.basename(file.name))[1]}"
    return data


def save(data: list, path: str, name: str, ret=False):
    if not os.path.exists(path):
        os.makedirs(path)
    paths = list()
    for i, file in enumerate(data):
        filename: str = f"{name}_{i}{os.path.splitext(file.filename)[1]}"
        path_save = os.path.join(path, filename)
        paths.append(filename)
        file.save(path_save)
    if ret:
        return paths


def save_card(form, mode: str, card_id=None) -> Response:
    from main import PATH
    from main import db_session
    from main import current_user

    db_sess = db_session.create_session()

    if mode == "edit":
        card = db_sess.get(Card, card_id)
        card.user = current_user
        card.title = form.title.data
        card.promt = form.promt.data

        db_sess.commit()
    else:
        card = Card()
        card.user = current_user
        card.title = form.title.data
        card.promt = form.promt.data
        db_sess.add(card)
        db_sess.commit()
        db_sess.flush()
        card_id = card.id

    db_sess.close()

    path_temp = os.path.join(PATH, f"data\\temp")
    file_names = os.listdir(path_temp)

    files = [os.path.join(path_temp, file) for file in file_names]

    path = os.path.join(PATH, f"data\\cards\\cards_{card_id}")
    delete_images(path)
    if not os.path.exists(path):
        os.makedirs(path)
    for file in files:
        shutil.copy(file, path)

    delete_images(path_temp)

    return redirect("/")


def reload_card(form, name: str, title: str) -> str:
    from main import PATH

    path_temp = os.path.join(PATH, f"data\\temp")
    delete_images(path_temp)
    save(form.images.data, path_temp, "card")
    file_names = os.listdir(path_temp)

    if file_names:
        return render_template(name, title=title, form=form, files=file_names)
    return render_template(name, title=title, form=form)


def load_card(form, name: str, title: str, card_id: int) -> str:
    from main import PATH
    from main import db_session

    db_sess = db_session.create_session()

    card = db_sess.get(Card, card_id)
    form.title.data = card.title
    form.promt.data = card.promt

    path_cards = os.path.join(PATH, f"data\\cards\\cards_{card_id}")
    file_names = os.listdir(path_cards)
    files = [os.path.join(path_cards, file) for file in file_names]

    path_temp = os.path.join(PATH, f"data\\temp")
    for file in files:
        shutil.copy(file, path_temp)

    return render_template(name, title=title, form=form, files=file_names)


def load_files(files_path: list) -> list:
    return [open(file, "rb") for file in files_path]


def delete_images(folder_path) -> None:
    try:
        files = os.listdir(folder_path)
        for file in files:
            file_path = os.path.join(folder_path, file)
            os.remove(file_path)
    except FileNotFoundError:
        pass
