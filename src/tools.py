from functools import wraps

from flask import session

from services.users import UsersService, UserDoesNotExistsError
from services.sellers import SellersService, SellerDoesNotExistsError
from src.database import db


def user_request_check(request_json: dict) -> bool:
    """Проверка наличия входных данных для создания пользователя"""
    if not all([
        request_json.get('email'),
        request_json.get('password'),
        request_json.get('first_name'),
        request_json.get('last_name'),
    ]):
        return False

    if request_json.get('is_seller') and not all([
        request_json.get('phone'),
        request_json.get('zip_code'),
        request_json.get('city_id'),
        request_json.get('street'),
        request_json.get('home'),
    ]):
        return False

    return True


def auth_required(func):
    """
    Декортатор для проверки авторизации пользователя.
    В случае успеха передаёт в декорируемую функцию словарь user с данными пользователя.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):

        user_id = session.get("user_id")
        if not user_id:
            return '', 403

        with db.connection as connection:

            user_service = UsersService(connection)
            try:
                user = user_service.read(user_id)
            except UserDoesNotExistsError:
                return '', 403

            return func(*args, **kwargs, user=user)
    return wrapper


def seller_required(func):
    """
    Декоратор для проверки авторизованного пользователя на наличие прав продавца.
    Используется совместно с декоратором @auth_required.
    В случае успеха предаёт в декорируемую функцию словарь user с данными пользователя.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):

        with db.connection as connection:
            seller_service = SellersService(connection)
            user = kwargs["user"]
            try:
                seller_id = seller_service.get_id(user_id=user["id"])
                user["seller_id"] = seller_id
            except SellerDoesNotExistsError:
                return '', 403

        return func(*args, **kwargs)
    return wrapper


def owner_required(func):
    """
    Декоратор для проверки авторизованного продавца на наличие прав для обращения к ресурсу.
    Используется совместно с декораторами @auth_required и @seller_required.
    В случае успеха предаёт в декорируемую функцию словарь user с данными пользователя.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):

        request_seller_id = kwargs["user"]["seller_id"]
        entry_ad_id = kwargs["ad_id"]

        with db.connection as connection:
            query = (
                """
                SELECT seller.id
                FROM ad
                    JOIN seller ON ad.seller_id = seller.id
                WHERE ad.id = ?
                """
            )
            params = (entry_ad_id, )

            cursor = connection.execute(query, params)
            result = cursor.fetchone()

            if result is None:
                return '', 403
            entry_seller_id = result["id"]

        if request_seller_id != entry_seller_id:
            return '', 403

        return func(*args, **kwargs)
    return wrapper
