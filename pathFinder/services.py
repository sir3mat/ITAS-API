import os
import random
from django.conf import settings
import igraph as ig

from .types import CarReq, Map, Maps, Road


class PathFinderService:
    def __init__(self):
        # read /static/maps.json file and create Maps object
        with open(os.path.join(settings.BASE_DIR, 'static/maps.json'), 'r') as f:
            json_string = f.read()
        self.maps = Maps(json_string)

    def getCarNumber(self, road: Road):
        return random.randint(0, 10)

    def getRoadLen(self, road: Road):
        return random.randint(0, 100)

    def computeWeight(self, carNumber, roadLen):
        return 10*carNumber + roadLen

    def mapToGraph(self, map: Map):
        edges = []
        weights = []
        for road in map.roads:
            # get sourceIntersection# and targetIntersection# (-1 is for index correctness for ig.graph)
            sourceId = int(road.source.replace("intersection", "")) - 1
            targetId = int(road.target.replace("intersection", "")) - 1

            edges.append((sourceId, targetId))
            # add random weight to edge (in real use case, we should use the number of cars in a road between two intersections)
            carNumber = self.getCarNumber(road)
            roadLen = self.getRoadLen(road)
            # compute a weight proportional to junction traffic and road length
            weight = self.computeWeight(carNumber, roadLen)
            weights.append(weight)
            assert len(weights) == len(edges)

        # create graph
        g = ig.Graph(
            len(map.intersections),
            edges,
            directed=True,
            vertex_attrs={
                'name': [ele + 1 for ele in range(len(map.intersections))], },
        )
        g.es['weight'] = weights

        return g

    def getAllPaths(self, g: ig.Graph, from_vertex: int, to_vertex: int):
        try:
            fromIndex = g.vs.find(name=from_vertex).index
            toIndex = g.vs.find(name=to_vertex).index
        except:
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
            res[idx] = [vertex+1 for vertex in path]
            print("Path {}: {}".format(idx, res[idx]))

        return res

    def createResponse(self, allPaths):
        obj = {}
        for key, value in allPaths.items():
            obj["pathId"] = key
            obj["path"] = ["intersection"+str(ele) for ele in value]
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
            g.es[g.ecount()-1]['weight'] = weight
        else:
            # update edge weight
            g.es[edge]['weight'] = weight

        return g

    def getPath(self, req: CarReq):
        # get map from maps object and set source and target vertex
        map = self.maps.mapList[req.mapId]
        from_vertex = req.fromIntersection
        to_vertex = req.toIntersection

        # create graph from map
        g = self.mapToGraph(map)

        # all shortest path
        allPaths = self.getAllPaths(g, from_vertex, to_vertex)

        if allPaths is None:
            return None

        res = self.createResponse(allPaths)
        return res
