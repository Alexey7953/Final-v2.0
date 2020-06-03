from flask.views import MethodView
from flask import Blueprint, jsonify, request

from src.database import db
from services.colors import ColorService

bp = Blueprint('color', __name__)


class ColorView(MethodView):

    def get(self):
        """ Получение списка всех цветов """
        with db.connection as connection:
            services_color = ColorService(connection)
            color = services_color.read_all_color()
            return jsonify(color), 200

    def post(self):
        """ Создание цвета """
        with db.connection as connection:
            name = request.json.get('name')
            hex_id = request.json.get('hex')
            services_color = ColorService(connection)
            color_id = services_color.create_color(name, hex_id)
            return jsonify(services_color.read_color(color_id)), 201


bp.add_url_rule('', view_func=ColorView.as_view('color'))
