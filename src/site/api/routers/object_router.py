import io
import os
import tempfile
import zipfile
from typing import List

import ifcopenshell
from PIL import Image
from flask import request, jsonify, send_file
from werkzeug.datastructures import FileStorage

import src.site.core.query_engines.object_query_engine as engine
from src.site.core.LibraryObject import LibraryObject

from flask import Blueprint

object_bp = Blueprint('object', __name__)


def create_temp_ifc_file(request_file: FileStorage) -> ifcopenshell.file:
    """
    Creates a temporary IFC file from an HTTP request so it can be handled

    :param requ
    est_file: file from the request
    :return: ifc file
    """
    content = request_file.read().decode("utf-8")
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as temp_file:
        temp_file.write(content)
        temp_file_path = temp_file.name
        return ifcopenshell.open(temp_file_path)


@object_bp.before_request
def _protect_object():
    if request.method == "OPTIONS":
        return "", 200


@object_bp.route('/', methods=['POST'])
def create_object_from_ifc():
    file = request.files['file']
    form_key_values = request.form.to_dict()

    if file:
        ifc_file = create_temp_ifc_file(file)
        customID = form_key_values["customID"] if "customID" in form_key_values else None

        response = engine.create_object(ifc_file, customID=customID)
        result = response["result"]

        if result == "created":
            return jsonify({"message": "Object Created", "object_id": response["_id"]}), 201
        elif result == "updated":
            return jsonify({"message": "Object Updated", "object_id": response["_id"]}), 200

    return "No file provided", 400


@object_bp.route("/<object_id>", methods=['PUT'])
def update_object_from_ifc(object_id: str):
    file = request.files['file']

    if file:
        ifc_file = create_temp_ifc_file(file)
        engine.update_by_id(object_id, ifc_file)
        return "Object updated"
    return "Object updated"


@object_bp.route("/")
def get_all_objects():
    response_format = request.args.get("format", default="json", type=str)
    query_response = engine.get_all_objects(response_format)

    if response_format == "json":
        return jsonify(query_response)
    elif response_format == "zip":
        return send_objects_as_zip(query_response)
    else:
        return f"Format: {response_format} not supported", 400


@object_bp.route('/<object_id>', methods=['GET'])
def get_object(object_id: str):
    response_format = request.args.get("format", default="json", type=str)
    query_response = engine.get_file_by_object_id(object_id, response_format)

    print(f"Getting object {object_id}")

    if response_format == "json":
        return jsonify(query_response)
    elif response_format == "ifc":
        return send_file(query_response, as_attachment=True)
    else:
        return f"Format: {response_format} not supported", 400


@object_bp.route("/<object_id>/photo", methods=['GET'])
def get_object_photo(object_id: str):
    path = engine.get_file_by_object_id(object_id, "png")
    try:
        return send_file(path, as_attachment=True)
    except FileNotFoundError:
        return "Photo not found", 404


@object_bp.route("/<object_id>/photo", methods=['POST'])
def add_object_photo(object_id: str):
    file = request.files['file']

    if file:
        image = Image.open(file.stream)
        engine.add_object_photo(object_id, image)
        return "Photo added"
    return "No file provided"


@object_bp.route("/<object_id>", methods=['DELETE'])
def delete_object(object_id: str):
    engine.delete_by_id(object_id)
    return "Object deleted"


def send_objects_as_zip(objects: List[LibraryObject]):
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for object in objects:
            file_path = object.ifc_file_path
            if os.path.exists(file_path):
                zip_file.write(file_path, arcname=os.path.basename(file_path))

    zip_buffer.seek(0)

    # Send the zip file to the client
    return send_file(zip_buffer, as_attachment=True, download_name="files.zip", mimetype="application/zip")


@object_bp.route("/filter", methods=['GET'])
def get_object_by_filter():
    response_format = request.args.get("format", default="json", type=str)
    query_params_dict = request.args.to_dict()

    found_objects = engine.get_by_filter(query_params_dict)

    if response_format == "json":
        return jsonify(found_objects)
    elif response_format == "zip":
        send_objects_as_zip(found_objects)
    else:
        pass  # TODO handle this


@object_bp.route("/nlp", methods=['GET'])
def get_object_by_nlp():
    response_format = request.args.get("format", default="json", type=str)
    nlp_query = request.get_json().get("query")
    found_objects = engine.get_by_nlp(nlp_query)
    if response_format == "json":
        return jsonify(found_objects)
    else:
        pass


@object_bp.route("/<object_id>/environmental-impact", methods=["GET"])
def get_environmental_impact_assessment(object_id: str):
    path = engine.get_environment_impact_assessment(object_id)
    try:
        return send_file(path, as_attachment=True)
    except FileNotFoundError:
        return "Environmental impact assessment not found", 404


@object_bp.route("/<object_id>/environmental-impact", methods=["POST"])
def add_environmental_impact_assessment(object_id: str):
    file = request.files['file']

    if file:
        engine.add_environmental_impact_assessment(file, object_id)
        return "Environmental impact assessment added"
    return "No file provided", 400


@object_bp.route("/<object_id>/manufacturers-booklet", methods=["GET"])
def get_manufacturers_booklet(object_id: str):
    path = engine.get_manufacturers_booklet(object_id)
    try:
        return send_file(path, as_attachment=True)
    except FileNotFoundError:
        return "Manufacturers booklet not found", 404


@object_bp.route("/<object_id>/manufacturers-booklet", methods=["POST"])
def add_manufacturers_booklet(object_id: str):
    file = request.files['file']

    if file:
        engine.add_manufacturers_booklet(file, object_id)
        return "Manufacturers booklet added"
    return "No file provided", 400


@object_bp.route("/<object_id>/inspection-record", methods=["GET"])
def get_inspection_record(object_id: str):
    date = request.args.get("date", default=None, type=str)
    path = engine.get_inspection_record(object_id, date)

    try:
        return send_file(path, as_attachment=True)
    except FileNotFoundError:
        return "Inspection record not found", 404


@object_bp.route("/<object_id>/inspection-record", methods=["POST"])
def add_inspection_record(object_id: str):
    file = request.files['file']
    date = request.form.get("date", default=None, type=str)

    if file:
        engine.add_inspection_record(file, object_id, date)
        return "Inspection record added"
    return "No file provided", 400


@object_bp.route("/<object_id>/inspection-record-dates", methods=["GET"])
def get_inspection_record_dates(object_id: str):
    dates = engine.get_inspection_record_dates(object_id)
    return jsonify(dates)


@object_bp.route("/manufacturer", methods=["GET"])
def get_all_manufacturers():
    manufacturers = engine.get_manufacturers()
    return jsonify(manufacturers)
