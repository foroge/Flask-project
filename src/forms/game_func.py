import os

from flask import render_template, redirect, Response

from data.db_session import SqlAlchemyBase
from werkzeug import Response

from data.cards import Card, CurrentCard
from data.user import User

from .card_func import load_random_card


def load_game(form) -> str:
    from main import PATH
    from main import db_session
    from main import current_user

    card = load_random_card()

    title = "Try to guess the card"
    found_card = "No cards found"
    if card:
        found_card = "Cards found!"
        db_sess = db_session.create_session()

        user_id = current_user.get_id()
        cur_card = db_sess.query(CurrentCard).filter(CurrentCard.user_id == user_id).first()
        current_card = cur_card if cur_card else CurrentCard()
        current_card.card_id = card["card_id"]
        current_card.user_id = current_user.get_id()

        db_sess.add(current_card) if not cur_card else ...
        db_sess.commit()
        db_sess.close()

        return render_template("game.html", title=title, form=form, data=card, found_card=found_card)
    return render_template("game.html", found_card=found_card)


def reload_game(form) -> Response | str:
    from main import PATH
    from main import db_session
    from main import current_user

    db_sess = db_session.create_session()

    user_id = current_user.get_id()
    current_card = db_sess.query(CurrentCard).filter(CurrentCard.user_id == user_id).first()
    if current_card:
        card = db_sess.get(Card, current_card.card_id)

        user = db_sess.get(User, user_id)
        if card.title.lower() == form.answer.data.lower():
            user.rating_user += 0.1
            title = False
            user.complited_cards.append(card)
        else:
            user.rating_user -= 0.1
            title = card.title
        if form.choices.data == "+":
            card.rating += 0.1
        elif form.choices.data == "-":
            card.rating -= 0.1
        db_sess.delete(current_card)
        db_sess.commit()
        db_sess.close()
        return redirect(f"/answer/{title}")
    db_sess.commit()
    db_sess.close()
    return load_game(form)
