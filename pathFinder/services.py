import os
import random
from django.conf import settings
import igraph as ig

from .types import CarReq, Lane, Map, Maps, OnlineReq, Road

SAVED_MAPS = {}


class PathFinderService:
    def getTrafficLightWeight(self, lane: Lane):
        state = lane.controlSignalState
        timeElapsed = lane.controlSignalTime
        redLightDuration = lane.redLightDuration + 0.01
        greenLightDuration = lane.greenLightDuration + 0.01

        if state == "red":
            timeFactor = (redLightDuration - timeElapsed) / redLightDuration
        else:
            timeFactor = timeElapsed / greenLightDuration
        return timeFactor

    def computeWeight(
        self, road: Road, lengthOnly, lane: Lane, considerTrafficLightMore: bool
    ):
        if lengthOnly:
            roadLen = road.length
            return roadLen
        else:
            if road.carsNumber == -1:
                return 1000000

            carNumber = lane.carsNumber
            roadLen = road.length
            if considerTrafficLightMore:
                trafficLightWeight = self.getTrafficLightWeight(lane)
                return trafficLightWeight * 30 * roadLen + carNumber
            else:
                trafficLightWeight = self.getTrafficLightWeight(lane)
                return roadLen + 30 * carNumber

    # def mapToGraph(self, current_map: Map, lengthOnly=False):
    # edges = []
    # weights = []
    # # for road in current_map.roads:
    # #     # get sourceIntersection# and targetIntersection# (-1 is for index correctness for ig.graph)
    # #     sourceId = int(road.source.replace("intersection", "")) - 1
    # #     targetId = int(road.target.replace("intersection", "")) - 1
    # #     for laneId in range(0, len(road.lanesCarNumbers)):
    # #         edges.append((sourceId, targetId))
    # #         # compute a weight proportional to junction traffic and road length
    # #         weight = self.computeWeight(
    # #             road, lengthOnly, laneId)
    # #         weights.append(weight)
    # #         assert len(weights) == len(edges)

    # for road in current_map.roads:
    #     # get sourceIntersection# and targetIntersection# (-1 is for index correctness for ig.graph)
    #     sourceId = int(road.source.replace("intersection", "")) - 1
    #     targetId = int(road.target.replace("intersection", "")) - 1
    #     edges.append((sourceId, targetId))
    #     # compute a weight proportional to junction traffic and road length
    #     weight = self.computeWeight(road, lengthOnly)
    #     weights.append(weight)
    #     assert len(weights) == len(edges)

    # # create graph
    # g = ig.Graph(
    #     len(current_map.intersections),
    #     edges,
    #     directed=True,
    #     vertex_attrs={
    #         "name": [ele + 1 for ele in range(len(current_map.intersections))]
    #     },
    # )
    # return g
    def mapToGraph(
        self,
        current_map: Map,
        lengthOnly=False,
        trafficLightsToConsider: list[str] = [],
    ):
        g = ig.Graph(directed=True)
        for road in current_map.roads:
            for lane in road.lanes:
                g.add_vertex(name=lane.id_)

        for road in current_map.roads:
            for lane in road.lanes:
                for other_road in current_map.roads:
                    if (
                        other_road.source == road.target
                        and other_road.target != road.source
                    ):
                        for other_lane in other_road.lanes:
                            if other_lane.id_ != lane.id_:
                                g.add_edge(lane.id_, other_lane.id_)
                                if lane.id_ in trafficLightsToConsider:
                                    g.es[-1]["weight"] = self.computeWeight(
                                        road, lengthOnly, lane, True
                                    )
                                else:
                                    g.es[-1]["weight"] = self.computeWeight(
                                        road, lengthOnly, lane, False
                                    )
        return g

    def getShortestPath(
        self, currentMap: Map, g: ig.Graph, from_vertex: int, to_vertex: int
    ):
        try:
            fromIndex = g.vs.find(name=from_vertex).index
            toIndex = g.vs.find(name=to_vertex).index
        except Exception as e:
            print(f"Exception [getShortestPath]: {e}")
            return None

        shortest_path = g.get_shortest_paths(
            fromIndex, to=toIndex, weights="weight", mode="out"
        )
        print("Shortest path: {}".format(shortest_path))

        shortestPath_vs_ids = []
        for vertex in shortest_path[0]:
            print("Vertex: {}, {}".format(vertex, g.vs[vertex]["name"]))
            # get intersectionId from laneId
            for intersection in currentMap.intersections:
                for road in intersection.roads:
                    for lane in road.lanes:
                        if lane.id_ == g.vs[vertex]["name"]:
                            shortestPath_vs_ids.append(intersection.id_)
        print(shortestPath_vs_ids)
        if not shortest_path:
            print("End node could not be reached!")
            return None

        res = {
            1: shortestPath_vs_ids,
        }

        return res, shortest_path

    def visualizeGraph(self, g: ig.Graph, targetName, shortestPath):
        g.es["width"] = 0.5
        # pathList = shortestPath[1]
        # for i in range(len(pathList) - 1):
        #     edge = g.get_eid(pathList[i] - 1, pathList[i + 1] - 1)
        #     g.es[edge]["width"] = 3.0

        ig.plot(
            g,
            target=targetName,
            format="svg",
            bbox=(800, 800),
            layout="auto",
            vertex_color="steelblue",
            # vertex_label=[ele + 1 for ele in range(g.vcount())],
            vertex_shape="circle",
            edge_width=g.es["width"],
            edge_label=g.es["weight"],
            edge_curved=True,
            edge_color="#666",
            edge_align_label=True,
            edge_background="white",
        )

    def createResponse(self, allPaths, error):
        obj = {
            "status": "ok" if not error else "error",
            "message": "" if not error else error,
        }
        for key, value in allPaths.items():
            obj["pathId"] = key
            obj["path"] = [str(ele) for ele in value]
        return obj

    def getPath(self, req: CarReq):
        error = None
        try:
            # get map from maps object and set source and target vertex
            current_map = Map(req.mapId, SAVED_MAPS[req.mapId])
            from_vertex = req.fromIntersection
            to_vertex = req.toIntersection
            lengthOnly = req.lengthOnly

            # # get shortest path
            paths = []
            costs = []
            fromLaneIds = []
            toLaneIds = []

            for intersection in current_map.intersections:
                if str(intersection.id_).removeprefix("intersection") == (
                    str(from_vertex)
                ):
                    for road in intersection.roads:
                        for lane in road.lanes:
                            fromLaneIds.append(lane.id_)

                if str(intersection.id_).removeprefix("intersection") == (
                    str(to_vertex)
                ):
                    for road in intersection.roads:
                        for lane in road.lanes:
                            toLaneIds.append(lane.id_)

            # create graph from map
            g = self.mapToGraph(current_map, lengthOnly, fromLaneIds)

            for fromLaneId in fromLaneIds:
                for toLaneId in toLaneIds:
                    intersectionList, shortestPath = self.getShortestPath(
                        current_map,
                        g,
                        fromLaneId,
                        toLaneId,
                    )
                    shortest_path_weight = sum(
                        g.es[i]["weight"] for i in shortestPath[0]
                    )
                    paths.append((intersectionList, shortestPath))
                    costs.append(shortest_path_weight)

            shortestPath = paths[costs.index(min(costs))][1]
            intersectionList = paths[costs.index(min(costs))][0]

            if shortestPath is None:
                return None

            # if lengthOnly == False:
            #     self.visualizeGraph(g, "out.svg", shortestPath)

            res = self.createResponse(intersectionList, error)
            return res

        except Exception as e:
            error = f"Server Exception [getPath]: {e}"
            return error

    def getOnlinePath(self, req: OnlineReq):
        error = None
        try:
            # get map from maps object and set source and target vertex
            current_map = Map(req.mapId, SAVED_MAPS[req.mapId])
            fromLaneId = req.fromLaneId
            to_vertex = req.toIntersection
            lengthOnly = req.lengthOnly
            # create graph from map
            g = self.mapToGraph(current_map, lengthOnly)

            # # get shortest path
            paths = []
            costs = []
            fromLaneIds = [fromLaneId]
            toLaneIds = []

            for intersection in current_map.intersections:
                if str(intersection.id_).removeprefix("intersection") == (
                    str(to_vertex)
                ):
                    for road in intersection.roads:
                        for lane in road.lanes:
                            toLaneIds.append(lane.id_)

            for fromLaneId in fromLaneIds:
                for toLaneId in toLaneIds:
                    intersectionList, shortestPath = self.getShortestPath(
                        current_map,
                        g,
                        fromLaneId,
                        toLaneId,
                    )
                    shortest_path_weight = sum(
                        g.es[i]["weight"] for i in shortestPath[0]
                    )
                    paths.append((intersectionList, shortestPath))
                    costs.append(shortest_path_weight)

            shortestPath = paths[costs.index(min(costs))][1]
            intersectionList = paths[costs.index(min(costs))][0]

            if shortestPath is None:
                return None

            res = self.createResponse(intersectionList, error)
            return res

        except Exception as e:
            error = f"Server Exception [getPath]: {e}"
            return error
