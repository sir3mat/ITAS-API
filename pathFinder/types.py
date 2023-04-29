import json


class CarReq:
    def __init__(self, mapId, fromIntersection, toIntersection):
        self.mapId = mapId
        self.fromIntersection = fromIntersection
        self.toIntersection = toIntersection


class Road:
    def __init__(self, id_, details):
        self.id_ = id_
        self.source = details["source"]
        self.target = details["target"]


class Intersection:
    def __init__(self, id_, details):
        self.id_ = id_
        # self.controlSignals_flipMultiplier = details["controlSignals"]["flipMultiplier"]      # todo fix
        # self.controlSignals_phaseOffset = details["controlSignals"]["phaseOffset"]            # todo fix


class Map:
    intersections: list[Intersection]
    intersections: list[Road]

    def __init__(self, id_, details):
        self.id_ = id_
        self.mapId = id_

        self.intersections = []
        for key in details["intersections"].keys():
            intersectionsId = key
            intersectionsDetails = details["intersections"][intersectionsId]
            self.intersections.append(Intersection(
                intersectionsId, intersectionsDetails))

        self.roads = []
        for key in details["roads"].keys():
            roadId = key
            roadDetails = details["roads"][roadId]
            self.roads.append(Road(roadId, roadDetails))

        self.carsNumber = details["carsNumber"]
        self.time = details["time"]
        # self.controlSignals = details["controlSignals"]   # todo fix



class Maps:
    mapList: list[Map]

    def __init__(self, json_string):
        data = json.loads(json_string)
        self.mapList = []
        for key in data.keys():
            mapId = key
            details = data[mapId]
            self.mapList.append(Map(mapId, details))
