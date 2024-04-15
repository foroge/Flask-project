from flask_restful import reqparse, abort, Api, Resource
from .user import User


parser = reqparse.RequestParser()
parser.add_argument('login', required=True)
parser.add_argument('age', required=True, type=int)
parser.add_argument('email', required=True)
parser.add_argument('hashed_password', required=True)


def abort_if_users_not_found(users_id):
    session = db_session.create_session()
    users = session.query(User).get(users_id)
    if not users:
        abort(404, message=f"User {users_id} not found")


class UserResource(Resource):
    @staticmethod
    def get(users_id):
        abort_if_users_not_found(users_id)
        session = db_session.create_session()
        users = session.query(User).get(users_id)
        return jsonify({'users': users.to_dict(
            only=('login', 'age', 'email', "hashed_password"))})

    @staticmethod
    def delete(users_id):
        abort_if_users_not_found(users_id)
        session = db_session.create_session()
        users = session.query(User).get(users_id)
        session.delete(users)
        session.commit()
        return jsonify({'success': 'OK'})


class UserListResource(Resource):
    @staticmethod
    def get():
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [item.to_dict(
            only=('login', 'age', 'email', "hashed_password")) for item in users]})

    @staticmethod
    def post():
        args = parser.parse_args()
        session = db_session.create_session()
        user = User()
        user.login = args['login'],
        user.age = args['age'],
        user.email = args['email'],
        user.set_password(args['hashed_password'])
        session.add(users)
        session.commit()
        return jsonify({'id': user.id})
