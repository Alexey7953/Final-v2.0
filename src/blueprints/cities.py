from flask import (
    Blueprint,
    request,
    jsonify
)

from flask.views import MethodView

from services.cities import (
    CitiesService,
    CityCreationError,
    CityDoesNotExists
)

from src.database import db


bp = Blueprint('cities', __name__)


class CitiesView(MethodView):

    def get(self):
        """ Получение списка всех городов """
        with db.connection as connection:
            service = CitiesService(connection)
            cities = service.read_all()
            return jsonify(cities), 200

    def post(self):
        """ Создание нового города """

        name = request.json.get("name")

        with db.connection as connection:
            city = CitiesService(connection)

            try:
                return jsonify(city.read(name)), 200
            except CityDoesNotExists:
                city.create(name)
                return jsonify(city.read(name)), 201
            except CityCreationError:
                return '', 500


bp.add_url_rule('', view_func=CitiesView.as_view('cities'))
