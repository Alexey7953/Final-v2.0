from datetime import datetime
from flask import Blueprint, jsonify, request
from flask.views import MethodView

from database import db
from services.ads import AdsService, AdDoesNotExists
from services.cars import CarsService, CarDoesNotExists
from services.colors import ColorService
from services.image import ImageService
from services.tags import TagsService
from tools import auth_required, seller_required, owner_required

bp = Blueprint('ads', __name__)


def generation_ad_dict(ad_id: int) -> dict:
    """Формирование словаря представления объявления"""
    with db.connection as connection:
        ad_service = AdsService(connection)
        response = ad_service.read_ad(ad_id)

        car_service = CarsService(connection)
        response["car"] = car_service.read_car(ad_id=ad_id)

        color_service = ColorService(connection)
        response["car"]["color"] = color_service.read_all_color(ad_id=ad_id)

        image_service = ImageService(connection)
        response["car"]["images"] = image_service.read_image(ad_id=ad_id)

        tags_service = TagsService(connection)
        response["tags"] = tags_service.read_tag(ad_id=ad_id)
    return response


class AdsView(MethodView):
    def get(self):
        """Получение списка объявлений"""
        query_seller_id = request.args.get("seller_id")
        query_tags = request.args.get("tags")
        query_make = request.args.get("make")
        query_model = request.args.get("model")

        with db.connection as connection:
            ad_service = AdsService(connection)
            asd_id = ad_service.generation_id(seller_id=query_seller_id)

        ads = [generation_ad_dict(asd_id) for ad_id in asd_id]

        if query_make is not None:
            ads = list(filter(lambda x: x["car"]["make"] == query_make, ads))

        if query_model is not None:
            ads = list(filter(lambda x: x["car"]["make"] == query_make, ads))

        if query_tags is not None:
            query_tags = [tag.strip() for tag in query_tags.split(',')]
            ads = [
                ad
                for ad in ads
                for tag in ad["tags"]
                if tag in query_tags
            ]

        return jsonify(ads)

    @auth_required
    @seller_required
    def post(self, user):
        """Создание нового объявления"""
        request_json = request.json

        seller_id = user["seller_id"]
        title = request_json.get('title')
        data = datetime.now().strftime("%A, %d. %B %Y %I:%M%p")
        tags = request_json.get("tags")
        car = request_json.get("car")
        colors = car.get("color")
        image = car.get("image")

        with db.connection as connection:

            car_service = CarsService(connection)
            car_id = car_service.create(car)

            color_service = ColorService(connection)
            for color in colors:
                color_service.add_to_car_color(color, car_id)

            image_service = ImageService(connection)
            for image_data in image:
                image_service.update_image(image_data, car_id)

            ads_serivce = AdsService(connection)
            ad_id = ads_serivce.create_ad(seller_id, car_id, title, data)

            tag_service = TagsService(connection)
            for tag in tags:
                tag_service.add_to_ad(tag, ad_id)

        return jsonify(generation_ad_dict(ad_id)), 201


class AdView(MethodView):
    def get(self, ad_id):
        """Получение объявления с указанным id"""
        try:
            response = generation_ad_dict(ad_id)
        except AdDoesNotExists:
            return '', 404
        return jsonify(response)

    @auth_required
    @seller_required
    @owner_required
    def delete(self, ad_id, user):
        """Удаление объявления с указанным id"""
        with db.connection as connection:
            as_service = AdsService(connection)

            try:
                as_service.read_ad(ad_id)
            except AdDoesNotExists:
                pass
            else:
                as_service.delete_ad(ad_id)

            return '', 200

    @auth_required
    @seller_required
    @owner_required
    def patch(self, ad_id, user):
        """Частичное редактирование объявления с указанным id"""
        request_json = request.json
        car_data = request_json.get("car")

        with db.connection as connection:

            title = request_json.get("title")
            if title is not None:
                as_service = AdsService(connection)
                as_service.update_ad(ad_id=ad_id, titile=title)

            tags = request_json["tags"]
            tags_service = TagsService(connection)
            for tag in tags:
                tags_service.add_to_ad(tag, ad_id)

            car_service = CarsService(connection)
            car_id = car_service.get_id(ad_id=ad_id)
            try:
                car_service.update(car_id=car_id, data=car_data)
            except CarDoesNotExists:
                car_service.create(car_data)

            colors = car_data.get("colors")
            car_service = ColorService(connection)
            for color in colors:
                car_service.add_to_car_color(color, car_id)

            images = car_data.get("images")
            image_service = ImageService(connection)
            for image in images:
                image_service.update_image(image, car_id)

        return '', 204


bp.add_url_rule('', view_func=AdsView.as_view('ads'))
bp.add_url_rule('/<int:ad_id>', view_func=AdsView.as_view('ad'))
