import json


class CarReq:
    def __init__(self, mapId, fromIntersection, toIntersection, lengthOnly):
        self.mapId = mapId
        self.fromIntersection = fromIntersection
        self.toIntersection = toIntersection
        self.onlyLen = lengthOnly


class Lane:
    def __init__(self, obj):
        self.id_ = obj["id"]
        self.carsNumber = obj["carsNumber"]


class Road:
    def __init__(self, id_, details):
        self.id_ = id_
        self.source = details["source"]
        self.target = details["target"]
        self.length = details["length"]
        self.carsNumber = details["carsNumber"]
        self.lanesCarNumbers = details["lanesCarNumbers"]

        self.lanes = []
        for lane in details["lanes"]:
            self.lanes.append(Lane(lane))


class Intersection:
    def __init__(self, id_, details):
        self.id_ = id_
        # self.controlSignals_flipMultiplier = details["controlSignals"]["flipMultiplier"]      # todo fix
        # self.controlSignals_phaseOffset = details["controlSignals"]["phaseOffset"]            # todo fix


class Map:
    intersections: list[Intersection]
    roads: list[Road]

    def __init__(self, id_, details):
        self.id_ = id_
        self.mapId = id_
        self.intersections = []
        self.roads = []

        for intersectionId, intersectionDetails in details["intersections"].items():
            self.intersections.append(Intersection(intersectionId, intersectionDetails))

        for roadId, roadDetails in details["roads"].items():
            self.roads.append(Road(roadId, roadDetails))

        self.carsNumber = details["carsNumber"]
        self.time = details["time"]
        # self.controlSignals = details["controlSignals"]   # todo fix
