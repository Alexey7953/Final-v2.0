import sqlite3
from src.exceptions import ServiceError


class UsersServiceError(ServiceError):
    service = 'users'


class UserDoesNotExistsError(object):
    pass


class UserCreationError(object):
    pass


class UserUpdateError(object):
    pass


class UsersService:
    def __init__(self, connection):
        self.connection = connection

    def auth(self, email):
        """Авторизация: вход и выход."""
        query = (
            """
            SELECT id, email, password
            FROM account
            WHERE email = ?
            """
        )
        params = (email,)

        cursor = self.connection.execute(query, params)
        auth_data = cursor.fetchone()

        if auth_data is None:
            raise UserDoesNotExistsError
        return dict(auth_data)

    def read(self, user_id):
        """Чтение данных пользователя"""
        query = (
            """
            SELECT id, first_name, last_name, email
            FROM account
            WHERE account.id = ?
            """
        )

        params = (user_id,)

        cursor = self.connection.execute(query, params)
        user = cursor.fetchone()
        if user is None:
            raise UserDoesNotExistsError
        return dict(user)

    def create(self, user_data):
        """Запись нового пользователя в базу"""

        query = (
            """
            INSERT INTO account (email, password, first_name, last_name) VALUES (?, ?, ?, ?)
            """
        )
        params = (
            user_data["email"],
            user_data["password"],
            user_data["first_name"],
            user_data["last_name"],
        )

        try:
            cursor = self.connection.execute(query, params)
            self.connection.commit()
        except sqlite3.IntegrityError:
            raise UserCreationError
        else:
            return cursor.lastrowid

    def update(self, user_id, data):
        """Частичное изменение пользователя."""

        new_data = {
            "first_name": data.get("first_name"),
            "last_name": data.get("last_name")
        }

        keys = ','.join(f'{key} = ?' for key in new_data if new_data[key] is not None)
        values = [value for value in new_data.values() if value is not None]

        query = f'UPDATE account SET {keys} WHERE id = ?'
        params = (*values, user_id)

        try:
            self.connection.execute(query, params)
            self.connection.commit()
        except sqlite3.IntegrityError:
            raise UserUpdateError
