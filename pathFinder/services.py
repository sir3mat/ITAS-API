import os
import random
from django.conf import settings
import igraph as ig

from .types import CarReq, Map, Maps, Road

SAVED_MAPS = {}


class PathFinderService:
    def getCarNumber(self, road: Road):
        return road.carsNumber

    def getRoadLen(self, road: Road):
        return road.length

    def computeWeight(self, road: Road, lengthOnly=False):
        if lengthOnly:
            roadLen = self.getRoadLen(road)
            return roadLen
        else:
            carNumber = self.getCarNumber(road)
            roadLen = self.getRoadLen(road)
            return 10 * carNumber + roadLen  # add semaphores weight

    def mapToGraph(self, current_map: Map, lengthOnly=False):
        edges = []
        weights = []
        for road in current_map.roads:
            # get sourceIntersection# and targetIntersection# (-1 is for index correctness for ig.graph)
            sourceId = int(road.source.replace("intersection", "")) - 1
            targetId = int(road.target.replace("intersection", "")) - 1

            edges.append((sourceId, targetId))
            # compute a weight proportional to junction traffic and road length
            weight = self.computeWeight(road, lengthOnly)
            weights.append(weight)
            assert len(weights) == len(edges)

        # create graph
        g = ig.Graph(
            len(current_map.intersections),
            edges,
            directed=True,
            vertex_attrs={
                'name': [ele + 1 for ele in range(len(current_map.intersections))], },
        )
        g.es['weight'] = weights
        return g

    def getAllPaths(self, g: ig.Graph, from_vertex: int, to_vertex: int):
        try:
            fromIndex = g.vs.find(name=from_vertex).index
            toIndex = g.vs.find(name=to_vertex).index
        except Exception as e:
            print(f"Exception [getAllPaths]: {e}")
            return None

        all_paths = g.get_all_shortest_paths(
            fromIndex,
            to=toIndex,
            weights='weight',
            mode='out'
        )
        if not all_paths:
            print("End node could not be reached!")
            return None

        res = {}
        for idx, path in enumerate(all_paths, start=1):
            res[idx] = [vertex + 1 for vertex in path]
            print("Path {}: {}".format(idx, res[idx]))

        return res

    def getShortestPath(self, g: ig.Graph, from_vertex: int, to_vertex: int):
        try:
            fromIndex = g.vs.find(name=from_vertex).index
            toIndex = g.vs.find(name=to_vertex).index
        except Exception as e:
            print(f"Exception [getShortestPath]: {e}")
            return None

        shortest_path = g.get_shortest_paths(
            fromIndex,
            to=toIndex,
            weights='weight',
            mode='out'
        )
        if not shortest_path:
            print("End node could not be reached!")
            return None

        res = {}
        for idx, path in enumerate(shortest_path, start=1):
            res[idx] = [vertex + 1 for vertex in path]
            print("Path {}: {}".format(idx, res[idx]))

        return res

    def createResponse(self, allPaths, error):
        obj = {
            "status": "ok" if not error else "error",
            "message": "" if not error else error,
        }
        for key, value in allPaths.items():
            obj["pathId"] = key
            obj["path"] = ["intersection" + str(ele) for ele in value]
        return obj

    def updateGraph(self, g: ig.Graph, road: Road):
        # get sourceIntersection# and targetIntersection# (-1 is for index correctness for ig.graph)
        sourceId = int(road.source.replace("intersection", "")) - 1
        targetId = int(road.target.replace("intersection", "")) - 1

        # add random weight to edge (in real use case, we should use the number of cars in a road between two intersections)
        carNumber = self.getCarNumber(road)
        roadLen = self.getRoadLen(road)
        # compute a weight proportional to junction traffic and road length
        weight = self.computeWeight(carNumber, roadLen)

        # check if edge exists
        edge = g.get_eid(sourceId, targetId, directed=True, error=False)
        if edge == -1:
            # add edge
            g.add_edge(sourceId, targetId)
            g.es[g.ecount() - 1]['weight'] = weight
        else:
            # update edge weight
            g.es[edge]['weight'] = weight

        return g

    def getPath(self, req: CarReq, lengthOnly=False):
        error = None
        try:
            # get map from maps object and set source and target vertex
            current_map = Map(req.mapId, SAVED_MAPS[req.mapId])
            from_vertex = req.fromIntersection
            to_vertex = req.toIntersection

            # create graph from map
            g = self.mapToGraph(current_map, lengthOnly)

            # all shortest path
            # allPaths = self.getAllPaths(g, from_vertex, to_vertex)
            # get shortest path
            allPaths = self.getShortestPath(g, from_vertex, to_vertex)
            if allPaths is None:
                return None
        except Exception as e:
            error = f"Server Exception [getPath]: {e}"

        res = self.createResponse(allPaths, error)
        return res
