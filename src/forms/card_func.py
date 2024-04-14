import os
import shutil

from flask import render_template, redirect, Response
from sqlalchemy.sql.expression import func

from data.db_session import SqlAlchemyBase
from data.cards import Card
from data.user import User


def name_change(data: list, name: str):
    for i, file in enumerate(data):
        file.name = f"{name}_{i}{os.path.splitext(os.path.basename(file.name))[1]}"
    return data


def save(data: list, path: str, name: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)
    for i, file in enumerate(data):
        filename: str = f"{name}_{i}{os.path.splitext(file.filename)[1]}"
        path_save = os.path.join(path, filename)
        file.save(path_save)


def load_files(files_path: list) -> list:
    return [open(file, "rb") for file in files_path]


def delete_images(folder_path: str) -> None:
    try:
        files = os.listdir(folder_path)
        for file in files:
            file_path = os.path.join(folder_path, file)
            os.remove(file_path)
    except FileNotFoundError:
        pass


def load_random_card() -> dict[str, str, list, int, int]:
    from main import current_user
    from main import db_session

    db_sess = db_session.create_session()

    user = db_sess.get(User, current_user.get_id())
    card = db_sess.query(Card).filter(Card.id not in user.complited_cards).order_by(func.random()).first()
    if card:
        from main import PATH
        path_cards = f"data\\cards\\cards_{card.id}"
        path_images = os.path.join(PATH, path_cards)
        paths = [f"cards_{card.id}/{path}" for path in os.listdir(os.path.join(PATH, path_images))]
        data = dict(title=card.title, promt=card.promt, paths=paths, rating=card.rating, card_id=card.id)
        return data


def save_card(form: SqlAlchemyBase, mode: str, card_id=None) -> Response:
    from main import PATH
    from main import db_session
    from main import current_user

    db_sess = db_session.create_session()

    card = Card() if mode != "edit" else db_sess.get(Card, card_id)
    card.user = current_user
    card.title = form.title.data
    card.promt = form.promt.data
    db_sess.add(card) if mode != "edit" else ...
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


