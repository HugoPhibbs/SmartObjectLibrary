from typing import TypedDict


class ConnectionCleatData(TypedDict):
    width: float
    length: float
    thickness: float


class ConnectionBoltData(TypedDict):
    total_top: int
    total_bottom: int
    diameter: float


class ConnectionFilletWeldData(TypedDict):
    flange: int
    web: int


class ConnectionDesignCapacityData(TypedDict):
    moment_top: float
    moment_bottom: float
    shear: float


class ConnectionConnectionData(TypedDict):
    cleat: ConnectionCleatData
    bolts: ConnectionBoltData
    fillet_welds: ConnectionFilletWeldData


class ConnectionData(TypedDict):
    connection_connection: ConnectionConnectionData
    design_capacity: ConnectionDesignCapacityData


MassToConnectionData = dict[str, ConnectionData]
MemberToMassToConnectionData = dict[str, MassToConnectionData]


class Connection:
    type: str = None
    data: dict = ConnectionData

    def __init__(self, type, data):
        self.type = type
        self.data = data