import os
from services.image import ImageService
from src.database import db
from flask import Blueprint, request, jsonify, url_for, send_file

bp = Blueprint('image', __name__)
upload_folder = 'download'


@bp.route('', methods=['POST'])
def post_image():
    """Загрузка изображения на сервер"""
    file = request.files['file']
    if file:
        if not os.path.exists(upload_folder):
            os.mkdir(upload_folder)

        file_name = file.filename
        file.save(os.path.join(upload_folder, file_name))
        url = url_for('image.get_image', name=file_name)
        with db.connection as connection:
            image_service = ImageService(connection)
            image_service.create_image(url)
        return jsonify({'url': url}), 201
    return '', 204


@bp.route('<name>', methods=["GET"])
def get_image(name):
    """Загрузка изображения с сервера"""
    return send_file(os.path.join('upload_folder', name))
