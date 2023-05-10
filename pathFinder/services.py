import igraph as ig
from pathFinder.types import CarReq, Map, Road

SAVED_MAPS = {}


class PathFinderService:
    # def getCarNumber(self, road: Road, laneId=0):
    #     return road.lanesCarNumbers[laneId]

    def getCarNumber(self, road: Road):
        sum = (road.lanesCarNumbers[0] + road.lanesCarNumbers[1]) // 2
        return sum

    def getRoadLen(self, road: Road):
        return road.length

    def computeWeight(self, road: Road, lengthOnly=False, laneId=0):
        if lengthOnly:
            roadLen = self.getRoadLen(road)
            return roadLen
        else:
            # carNumber = self.getCarNumber(road, laneId)
            carNumber = self.getCarNumber(road)
            roadLen = self.getRoadLen(road)
            return 30 * carNumber + roadLen  # add semaphores weight

    def mapToGraph(self, current_map: Map, lengthOnly=False):
        edges = []
        weights = []
        # for road in current_map.roads:
        #     # get sourceIntersection# and targetIntersection# (-1 is for index correctness for ig.graph)
        #     sourceId = int(road.source.replace("intersection", "")) - 1
        #     targetId = int(road.target.replace("intersection", "")) - 1
        #     for laneId in range(0, len(road.lanesCarNumbers)):
        #         edges.append((sourceId, targetId))
        #         # compute a weight proportional to junction traffic and road length
        #         weight = self.computeWeight(
        #             road, lengthOnly, laneId)
        #         weights.append(weight)
        #         assert len(weights) == len(edges)

        for road in current_map.roads:
            # get sourceIntersection# and targetIntersection# (-1 is for index correctness for ig.graph)
            sourceId = int(road.source.replace("intersection", "")) - 1
            targetId = int(road.target.replace("intersection", "")) - 1
            edges.append((sourceId, targetId))
            # compute a weight proportional to junction traffic and road length
            weight = self.computeWeight(
                road, lengthOnly)
            weights.append(weight)
            assert len(weights) == len(edges)

        # create graph
        g = ig.Graph(
            len(current_map.intersections),
            edges,
            directed=True,
            vertex_attrs={
                'name': [ele + 1 for ele in range(len(current_map.intersections))]},
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

    def visualizeGraph(self, g: ig.Graph, targetName, shortestPath):
        g.es['width'] = 0.5
        pathList = shortestPath[1]
        for i in range(len(pathList) - 1):
            edge = g.get_eid(pathList[i] - 1, pathList[i + 1] - 1)
            g.es[edge]['width'] = 3.0

        ig.plot(
            g,
            target=targetName,
            format='svg',
            bbox=(800, 800),
            layout="kk",
            vertex_color='steelblue',
            vertex_label=[ele + 1 for ele in range(g.vcount())],
            vertex_shape='circle',
            edge_width=g.es['width'],
            edge_label=g.es["weight"],
            edge_curved=True,
            edge_color='#666',
            edge_align_label=True,
            edge_background='white'
        )

    def createResponse(self, allPaths, error):
        obj = {
            "status": "ok" if not error else "error",
            "message": "" if not error else error,
        }
        for key, value in allPaths.items():
            obj["pathId"] = key
            obj["path"] = ["intersection" + str(ele) for ele in value]
        return obj

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
            shortestPath = self.getShortestPath(g, from_vertex, to_vertex)
            if shortestPath is None:
                return None
        except Exception as e:
            error = f"Server Exception [getPath]: {e}"

        if lengthOnly == False:
            self.visualizeGraph(g, "out.svg", shortestPath)
        res = self.createResponse(shortestPath, error)
        return res
