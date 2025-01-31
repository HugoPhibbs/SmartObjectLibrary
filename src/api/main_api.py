import io
import os

import ifcopenshell
from flask import Flask, request, jsonify, send_file
import src.core.query_engine as engine
import zipfile
import tempfile

app = Flask(__name__)


def create_temp_ifc_file(request_file):
    content = request_file.read().decode("utf-8")
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as temp_file:
        temp_file.write(content)
        temp_file_path = temp_file.name
        return ifcopenshell.open(temp_file_path)


@app.route('/object', methods=['POST'])
def create_object():
    file = request.files['file']

    if file:
        ifc_file = create_temp_ifc_file(file)
        engine.create_object(ifc_file)

        return "Object created"

    return "No file provided"


@app.route("/object/<object_id>", methods=['PUT'])
def update_object(object_id: int):
    file = request.files['file']

    if file:
        ifc_file = create_temp_ifc_file(file)
        engine.update_by_id(object_id, ifc_file)
        return "Object updated"
    return "Object updated"


@app.route("/object")
def get_all_objects():
    response_format = request.args.get("format", default="json", type=str)
    query_response = engine.get_all_objects(response_format)

    if response_format == "json":
        return jsonify(query_response)
    elif response_format == "zip":
        return send_objects_as_zip(query_response)
    else:
        pass


@app.route('/object/<object_id>', methods=['GET'])
def get_object(object_id: int):
    response_format = request.args.get("format", default="json", type=str)
    query_response = engine.get_by_id(object_id, response_format)

    if response_format == "json":
        return jsonify(query_response)
    elif response_format == "ifc":
        return send_file(query_response, as_attachment=True)
    else:
        pass  # TODO handle this


@app.route("/object/<object_id>", methods=['DELETE'])
def delete_object(object_id: int):
    engine.delete_by_id(object_id)
    return "Object deleted"


def send_objects_as_zip(objects):
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for object in objects:
            file_path = object["ifc_file_path"]
            if os.path.exists(file_path):
                zip_file.write(file_path, arcname=os.path.basename(file_path))

    zip_buffer.seek(0)

    # Send the zip file to the client
    return send_file(zip_buffer, as_attachment=True, download_name="files.zip", mimetype="application/zip")


@app.route("/object/filter", methods=['GET'])
def get_object_by_filter():
    response_format = request.args.get("format", default="json", type=str)
    object_filter = request.get_json().get("filter")
    found_objects = engine.get_by_filter(object_filter)
    if response_format == "json":
        return jsonify(found_objects)
    elif response_format == "zip":
        send_objects_as_zip(found_objects)
    else:
        pass  # TODO handle this


@app.route("/object/nlp", methods=['GET'])
def get_object_by_nlp():
    response_format = request.args.get("format", default="json", type=str)
    nlp_query = request.get_json().get("query")
    found_objects = engine.get_by_nlp(nlp_query)
    if response_format == "json":
        return jsonify(found_objects)
    else:
        pass


if __name__ == '__main__':
    app.run(debug=True)
