from flask import Flask, request, jsonify
import src.core.query_engine as engine

app = Flask(__name__)


@app.route('/object', methods=['POST'])
def create_object():
    new_object_data = request.get_json()
    engine.create_object(new_object_data)
    return "Object created"


@app.route('/object/<id>', methods=['GET'])
def get_object(object_id: int):
    response_format = request.args.get("format", default="json", type=str)
    found_object = engine.get_by_id(object_id)
    if response_format == "json":
        return jsonify(found_object)
    else:
        pass  # TODO return IFC file


@app.route("/object/<id>", methods=['DELETE'])
def delete_object(object_id: int):
    engine.delete_by_id(object_id)
    return "Object deleted"


@app.route("/object/<id>", methods=['PUT'])
def update_object(object_id: int):
    new_object_data = request.get_json()
    engine.update_by_id(object_id, new_object_data)
    return "Object updated"


@app.route("/object/filter", methods=['GET'])
def get_object_by_filter():
    response_format = request.args.get("format", default="json", type=str)
    object_filter = request.get_json().get("filter")
    found_objects = engine.get_by_filter(object_filter)
    if response_format == "json":
        return jsonify(found_objects)
    else:
        pass  # TODO return IFC files


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
    app.run()
