import json

class OnlineReq:
    def __init__(self, mapId, fromLaneId, toIntersection, lengthOnly):
        self.mapId = mapId
        self.fromLaneId = fromLaneId
        self.toIntersection = toIntersection
        self.lengthOnly = lengthOnly


class CarReq:
    def __init__(self, mapId, fromIntersection, toIntersection, lengthOnly):
        self.mapId = mapId
        self.fromIntersection = fromIntersection
        self.toIntersection = toIntersection
        self.lengthOnly = lengthOnly


class Lane:
    def __init__(self, obj):
        self.id_ = obj["id"]
        self.carsNumber = obj["carsNumber"]
        self.controlSignalState = obj["controlSignalState"]
        self.greenLightDuration = obj["greenLightDuration"]
        self.redLightDuration = obj["redLightDuration"]
        self.controlSignalTime = obj["controlSignalTime"]


class Road:
    def __init__(self, id_, details):
        self.id_ = id_
        self.source = details["source"]
        self.target = details["target"]
        self.length = details["length"]
        self.carsNumber = details["carsNumber"]
        self.lanes = []
        for lane in details["lanes"]:
            self.lanes.append(Lane(lane))


class Intersection:
    inRoads: list[Road]
    roads: list[Road]

    def __init__(self, id_, details):
        self.id_ = id_
        self.inRoads = []
        self.roads = []

        for road in details["roads"]:
            roadId = road["id"]
            source = road["source"]
            target = road["target"]
            length = road["length"]
            carsNumber = road["carsNumber"]
            lanes = road["lanes"]
            obj = {
                "id": roadId,
                "source": source,
                "target": target,
                "length": length,
                "carsNumber": carsNumber,
                "lanes": lanes,
            }
            self.roads.append(Road(roadId, obj))

        for road in details["inRoads"]:
            roadId = road["id"]
            source = road["source"]
            target = road["target"]
            length = road["length"]
            carsNumber = road["carsNumber"]
            lanes = road["lanes"]
            obj = {
                "id": roadId,
                "source": source,
                "target": target,
                "length": length,
                "carsNumber": carsNumber,
                "lanes": lanes,
            }
            self.inRoads.append(Road(roadId, obj))


class Map:
    intersections: list[Intersection]
    roads: list[Road]

    def __init__(self, id_, details):
        self.id_ = id_
        self.mapId = id_
        self.intersections = []
        for key in details["intersections"].keys():
            intersectionsId = key
            intersectionsDetails = details["intersections"][intersectionsId]
            self.intersections.append(
                Intersection(intersectionsId, intersectionsDetails)
            )

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
