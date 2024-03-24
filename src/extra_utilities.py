import os
import json
from flask import render_template
#
#
def json_save(file_path, path, data):
    pass
    # with open(file_path) as file:
    #     json.dump(data)


def name_change(data, name):
    for i, file in enumerate(data):
        file.filename = f"{name}_{i}{os.path.splitext(file.filename)[1]}"
    return data


def save(data: list, path: str, ret=False):
    if not os.path.exists(path):
        os.makedirs(path)
    paths = list()
    for i, file in enumerate(data):
        path_save = os.path.join(path, file.filename)
        path.append(path_save)
        file.save(path_save)
    if ret:
        return paths


def save_card(form):
    db_sess = db_session.create_session()

    card = Card()
    card.user = current_user
    card.title = form.title.data
    card.promt = form.promt.data

    db_sess.add(card)
    db_sess.commit()
    db_sess.refresh(card)
    db_sess.close()

    path = os.path.join(PATH, f"data\\cards\\cards_{card.id}")
    data = name_change(form.images.data, "card")
    save(data, path)

    return redirect("/")


def reload_card(form, name, title):
    path = os.path.join(PATH, f"data\\temp")
    data = name_change(form.images.data, "card")
    paths = save(data, path, ret=True)
    if paths:
        return render_template(name, title=title, form=form, files=paths)
    return render_template(name, title=title, form=form)

