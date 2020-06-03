from flask import Blueprint, request, session
from werkzeug.security import check_password_hash
from services.users import UsersService, UserDoesNotExistsError
from src.database import db

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['POST'])
def login():
    """Авторизация пользователя"""
    request_json = request.json
    email = request_json.get('email')
    password = request_json.get('password')

    if not email or not password:
        return '', 400

    with db.connection as connection:
        user_service = UsersService(connection)
        try:
            user_data = user_service.auth(email=email)
        except UserDoesNotExistsError:
            return '', 404
        else:
            user_email = user_data["email"]
            user_password_hash = user_data["password"]
            user_id = user_data["id"]

    if not (
            email == user_email
            and
            check_password_hash(user_password_hash, password)
    ):
        return '', 403

    session['user_id'] = user_id
    return '', 200


@bp.route('/logout', methods=['POST'])
def logout():
    """Завершение текущей сессии"""
    session.pop('user_id', None)
    return '', 200
