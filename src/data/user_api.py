import flask
from . import db_session
from flask import jsonify, make_response, request
from .user import User
from requests import post

from main import path_templates

blueprint = flask.Blueprint(
        'users_api',
        __name__,
        template_folder=path_templates
    )


@blueprint.route('/api/users')
def get_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return jsonify(
        {
            'users':
                [item.to_dict(only=('login', 'age', "email", "rating_whole", "rating_user",
                                    "hashed_password")) for item in users]
        }
    )


@blueprint.route('/api/users/<int:user_id>', methods=['GET'])
def get_one_user(user_id):
    db_sess = db_session.create_session()
    users = db_sess.query(User).get(user_id)
    if not users:
        return make_response(jsonify({'error': 'Not found'}), 404)
    return jsonify(
        {
            'users':
                users.to_dict(only=('login', 'age', "email", "rating_whole", "rating_user",
                                    "hashed_password"))
        }
    )


@blueprint.route('/api/users', methods=['POST'])
def create_users():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in request.json for key in
                 ['login', 'age', "email", "hashed_password"]):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    elif not 0 <= int(request.json['age']) <= 130:
        return make_response(jsonify({'error': 'Bad request'}), 400)

    users = User()
    users.login = request.json['login']
    users.age = request.json['age']
    users.email = request.json['email']
    users.set_password(request.json['hashed_password'])

    db_sess = db_session.create_session()
    db_sess.add(users)
    db_sess.commit()
    return jsonify({'id': users.id})


@blueprint.route('/api/users/<int:users_id>', methods=['DELETE'])
def delete_users(users_id):
    db_sess = db_session.create_session()
    users = db_sess.query(User).get(users_id)
    if not users:
        return make_response(jsonify({'error': 'Not found'}), 404)
    db_sess.delete(users)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/users/<int:users_id>', methods=['PUT'])
def edit_users(users_id):
    char = ['login', 'age', "email", "hashed_password"]
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in char for key in request.json):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(users_id)
    for key in request.json:
        if key != "hashed_password":
            setattr(user, key, request.json[key])
        else:
            user.set_password(request.json[key])
    db_sess.commit()
    return jsonify({'id': user.id})