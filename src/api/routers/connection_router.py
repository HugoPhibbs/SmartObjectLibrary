from flask import Blueprint, request

import src.core.query_engines.connection_query_engine as query_engine

connection_bp = Blueprint('connection', __name__)


@connection_bp.route('/<connection_id>', methods=['GET'])
def get_connection(connection_id: str):
    print(connection_id)
    connection = query_engine.get_connection_by_id(connection_id)
    return connection, 200 if connection else None, 404


@connection_bp.route("/filter", methods=["GET"])
def get_connections_by_filter():
    query_params = request.args.to_dict()

    results = query_engine.get_connections_by_filter(query_params)
    return results, 200


@connection_bp.route("/", methods=['GET'])
def get_all_connections():
    connections = query_engine.get_all_connections()
    return connections, 200

@connection_bp.route("/unique-values", methods=['GET'])
def get_unique_fields_values():
    field = request.args.get("field", default=None)
    unique_values = query_engine.get_unique_values(field)
    return unique_values, 200