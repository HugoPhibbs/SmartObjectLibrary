import io
import os
import tempfile
import zipfile
from typing import List

import ifcopenshell
from flask import request, jsonify, send_file
from werkzeug.datastructures import FileStorage

from src.site.core.cloud.opensearch import get_os_client
from src.site.core.QueryBuilder import QueryBuilder
from src.site.core.cloud.ObjectLibraryBucket import ObjectLibraryBucket
from src.site.core.cloud.ObjectsOSIndex import ObjectsOSIndex
from src.site.api.auth import check_auth
from src.site.core.LibraryObject import LibraryObject

from flask import Blueprint

object_bp = Blueprint('object', __name__)

s3_bucket = ObjectLibraryBucket("object-library-files")
os_index = ObjectsOSIndex()

os_client = get_os_client()


def filestorage_to_buffer(file_storage):
    buf = io.BytesIO()
    file_storage.save(buf)
    buf.seek(0)
    return buf


def create_temp_ifc_file(request_file: FileStorage) -> ifcopenshell.file:
    """
    Creates a temporary IFC file from an HTTP request so it can be handled

    :param request_file: file from the request
    :return: ifc file
    """
    content = request_file.read().decode("utf-8")
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as temp_file:
        temp_file.write(content)
        temp_file_path = temp_file.name
        return ifcopenshell.open(temp_file_path)


@object_bp.before_request
def _protect_object():
    return check_auth()


@object_bp.route('/', methods=['POST'])
def create_object_from_ifc():
    try:
        file = request.files['file']
    except KeyError:
        return "No file provided", 400

    form_key_values = request.form.to_dict()

    if file:
        ifc_file = create_temp_ifc_file(file)
        customID = form_key_values["customID"] if "customID" in form_key_values else None
        object_dict, object_id = LibraryObject.ifc_file_to_dict(ifc_file, customID=customID)

        os_response = os_client.put_object(object_id=object_id, object_data=object_dict)
        buffer = filestorage_to_buffer(file)
        s3_bucket.put_object_ifc(object_id, buffer)

        result = os_response["result"]

        if result == "created":
            return jsonify({"message": "Object Created", "object_id": os_response["_id"]}), 201
        elif result == "updated":
            return jsonify({"message": "Object Updated", "object_id": os_response["_id"]}), 200

    return "No file provided", 400


@object_bp.route("/<object_id>", methods=['PUT'])
def update_object_from_ifc(object_id: str):
    file = request.files['file']

    if file:
        ifc_file = create_temp_ifc_file(file)
        object_dict, _ = LibraryObject.ifc_file_to_dict(ifc_file)

        os_index.put_object(object_id=object_id, object_data=object_dict)
        buffer = filestorage_to_buffer(file)
        s3_bucket.put_object_ifc(object_id, buffer, overwrite_existing=True)

        return "Object updated"
    return "Object updated"


@object_bp.route("/")
def get_all_objects():
    return os_index.get_all_objects()


@object_bp.route('/<object_id>', methods=['GET'])
def get_object(object_id: str):
    response_format = request.args.get("format", default="json", type=str)

    if response_format == "json":
        query_response = os_index.get_object(object_id=object_id)
    elif response_format == "ifc":
        query_response = s3_bucket.get_object_ifc(object_id)
    else:
        return f"Format: {response_format} not supported", 400

    if query_response is None:
        return "Object not found", 404

    return query_response


@object_bp.route("/<object_id>/photo", methods=['GET'])
def get_object_photo(object_id: str):
    image_buffer = s3_bucket.get_object_photo(object_id)

    if image_buffer is None:
        return "Photo not found", 404

    return send_file(image_buffer, as_attachment=False, download_name=f"{object_id}.png", mimetype='image/png')


@object_bp.route("/<object_id>/photo", methods=['POST'])
def add_object_photo(object_id: str):
    file = request.files['file']

    if file:
        buffer = filestorage_to_buffer(file)
        s3_bucket.put_object_photo(object_id, buffer, True)
        return "Photo added"
    return "No file provided"


@object_bp.route("/<object_id>", methods=['DELETE'])
def delete_object(object_id: str):
    os_index.delete_object(object_id)
    s3_bucket.delete_objects_files(object_id)
    return "Object deleted", 200


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


@object_bp.route("/query", methods=['GET'])
def get_objects_by_filter():
    response_format = request.args.get("format", default="json", type=str)
    query_params_dict = request.args.to_dict()
    if "format" in query_params_dict:
        del query_params_dict["format"]

    os_query = QueryBuilder().from_query_params_dict(query_params_dict).build()

    print(os_query)

    found_objects = os_index.get_objects_by_query(os_query)

    if response_format == "json":
        return jsonify(found_objects)
    elif response_format == "zip":
        send_objects_as_zip(found_objects)
    else:
        pass  # TODO handle this


@object_bp.route("/os-query", methods=['GET'])
def get_object_by_os_query():
    os_query_params = request.get_json()  # Should be in OpenSearch Query DSL format

    os_query = {"query": os_query_params}

    found_objects = os_index.get_objects_by_query(os_query)

    return jsonify(found_objects)


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
    buffer = s3_bucket.get_environmental_impact_assessment(object_id)

    if buffer is not None:
        return send_file(buffer, as_attachment=True)
    else:
        return "Environmental Impact Assessment not found", 404


@object_bp.route("/<object_id>/environmental-impact", methods=["POST"])
def add_environmental_impact_assessment(object_id: str):
    file = request.files['file']

    if file:
        buffer = filestorage_to_buffer(file)
        s3_bucket.put_environmental_impact_assessment(object_id, buffer, overwrite_existing=True)
        return "Environmental impact assessment added"
    return "No file provided", 400


@object_bp.route("/<object_id>/manufacturers-booklet", methods=["GET"])
def get_manufacturers_booklet(object_id: str):
    buffer = s3_bucket.get_manufacturers_booklet(object_id)

    if buffer is not None:
        return send_file(buffer, as_attachment=True)
    else:
        return "Manufacturers booklet not found", 404


@object_bp.route("/<object_id>/manufacturers-booklet", methods=["POST"])
def add_manufacturers_booklet(object_id: str):
    file = request.files['file']

    if file:
        buffer = filestorage_to_buffer(file)
        s3_bucket.put_manufacturers_booklet(object_id, buffer, overwrite_existing=True)
        return "Manufacturers booklet added"
    return "No file provided", 400


@object_bp.route("/<object_id>/inspection-record", methods=["GET"])
def get_inspection_record(object_id: str):
    date = request.args.get("date", default=None, type=str)
    buffer = s3_bucket.get_inspection_record(object_id, date)

    if buffer is not None:
        return send_file(buffer, as_attachment=True)
    else:
        return "Inspection record not found", 404


@object_bp.route("/<object_id>/inspection-record", methods=["POST"])
def add_inspection_record(object_id: str):
    file = request.files['file']
    date = request.form.get("date", default=None, type=str)

    if file:
        buffer = filestorage_to_buffer(file)
        s3_bucket.put_inspection_record(object_id, date, buffer, overwrite_existing=True)
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


@object_bp.get("/wall-substitution")
def get_wall_substitution():
    pass