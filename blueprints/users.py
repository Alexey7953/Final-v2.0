from flask import Blueprint, jsonify, request
from flask.views import MethodView
from werkzeug.security import generate_password_hash

from src.database import db

from services.sellers import SellersService, SellerCreationError, SellerDoesNotExistsError
from services.users import UsersService, UserCreationError, UserDoesNotExistsError
from services.zipcode import ZipcodesCreationError, ZipcodesService
from src.tools import user_request_check

bp = Blueprint('users', __name__)


class UsersView(MethodView):
    def post(self):
        """Регистрация нового пользователя"""
        request_json = request.json

        if not user_request_check(request_json):
            return '', 400
        request_json["password"] = generate_password_hash(request_json["password"])

        with db.connection as connection:
            user_service = UsersService(connection)
            try:
                user_id = user_service.create(user_data=request_json)
            except UserCreationError:
                return '', 409

            user = user_service.read(user_id=user_id)
            user.update({
                "is_seller": request_json["is_seller"],
            })

            if user["is_seller"]:
                seller_service = SellersService(connection)
                zipcode_service = ZipcodesService(connection)
                try:
                    seller_id = seller_service.create(seller_data=request_json, user_id=user_id)
                    zipcode_service.create(Zipcode_data=request_json)
                except (SellerCreationError, ZipcodesCreationError):
                    return '', 409

                seller = seller_service.read(seller_id=seller_id)
                user.update(seller)

            return jsonify(user), 201


class UserView(MethodView):

    @auth_required
    def get(self, user_id, user):
        """Получение информации о пользователе по id"""
        with db.connection as connection:
            user_service = UsersService(connection)
            seller_service = SellersService(connection)
            try:
                user_data = user_service.read(user_id=user_id)
                seller_data = seller_service.read(user_id=user_id)
            except UserDoesNotExistsError:
                return '', 404
            except SellerDoesNotExistsError:
                return jsonify(user_data)
            else:
                user_data.update(seller_data)
                user_data.update({"is_seller": True})
                return jsonify(user_data)

    @auth_required
    def patch(self, user_id, user):
        """Частичное редактирование пользователя"""
        if not user_id == user["id"]:
            return '', 403

        request_json = request.json
        is_seller = request_json["is_seller"]

        with db.connection as connection:
            user_service = UsersService(connection)
            seller_service = SellersService(connection)
            zipcode_service = ZipcodesService(connection)
            car_service = CarsService(connection)

            user_service.update(user_id=user_id, data=request_json)
            zipcode_service.update(data=request_json)

            if is_seller:
                try:
                    seller_service.update(user_id=user_id, data=request_json)
                except SellerDoesNotExistsError:
                    seller_service.create(user_id=user_id, seller_data=request_json)
            else:
                seller_service.delete(user_id)
                try:
                    car_id = car_service.get_id(user_id=user_id)
                    car_service.delete(car_id)
                except CarDoesNotExists:
                    pass

        return self.get(user_id)


bp.add_url_rule('', view_func=UsersView.as_view('users'))
bp.add_url_rule('/<int:user_id>', view_func=UserView.as_view('user'))
