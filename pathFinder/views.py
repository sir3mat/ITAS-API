from rest_framework import status
from rest_framework.response import Response
from pathFinder.types import CarReq, Map
from rest_framework import generics
from pathFinder.services import PathFinderService, SAVED_MAPS
from drf_spectacular.utils import extend_schema
from pathFinder.serializers import GetPathsSerializer, PathResponseSerializer, ErrorResponseSerializer
import json
from django.urls import URLPattern, get_resolver
from django.http import HttpResponse


def api_urls(request):
    resolver = get_resolver(None)
    url_patterns = resolver.url_patterns
    api_urls = []

    def find_api_urls(url_patterns, base=''):
        for pattern in url_patterns:
            if isinstance(pattern, URLPattern):

                api_urls.append(base + str(pattern.pattern))
            else:
                # URLResolver
                if pattern.namespace:
                    base = pattern.namespace + '/'
                    if base == 'api/':
                        find_api_urls(pattern.url_patterns, base)
                # find_api_urls(pattern.url_patterns, base)     # this is for getting all urls

    find_api_urls(url_patterns)

    current_ip = request.build_absolute_uri('/')[:-1]
    response_content = f"""
    <h1>APIs</h1>
    <ul>
        {"".join([f"<li><a href='{current_ip}/{url}'>{url}</a></li>" for url in api_urls])}
    </ul>
    """
    return HttpResponse(response_content)


class PathFinderViewSet(generics.GenericAPIView):
    @extend_schema(
        parameters=[
            GetPathsSerializer
        ],
        responses={
            200: PathResponseSerializer,
            400: ErrorResponseSerializer,
        },
    )
    def get(self, request):
        mapId = request.query_params["mapId"]
        if mapId not in SAVED_MAPS:
            response = Response(
                {
                    "status": "error",
                    "message": "Map not found!",
                    "mapId": mapId
                }, status=status.HTTP_400_BAD_REQUEST)
            return response

        fromIntersection = int(request.query_params["fromIntersection"])
        toIntersection = int(request.query_params["toIntersection"])
        lengthOnly = request.query_params["lengthOnly"] == "true"
        pathFinder_service = PathFinderService()
        req = CarReq(mapId, fromIntersection, toIntersection, lengthOnly)
        res = pathFinder_service.getPath(req)
        if res is None:
            response = Response(
                {
                    "status": "error",
                    "message": "End node could not be reached!"
                }, status=status.HTTP_400_BAD_REQUEST)
            return response

        response = Response(res, status=status.HTTP_200_OK)
        return response


class MapViewSet(generics.GenericAPIView):

    def post(self, request):
        new_map = request.data.get('map')
        try:
            if new_map and json.loads(new_map):
                new_map = json.loads(new_map)
            else:
                raise json.decoder.JSONDecodeError
        except json.decoder.JSONDecodeError:
            response = Response(
                {
                    "status": "error",
                    "message": "Map not found!"
                }, status=status.HTTP_400_BAD_REQUEST)
            return response

        SAVED_MAPS[new_map["mapId"]] = new_map
        response = Response({
            "status": "ok",
            "message": "Map saved!"
        }, status=status.HTTP_200_OK)
        return response


class RoadsViewSet(generics.GenericAPIView):
    def patch(self, request):
        mapId = request.data.get('mapId')
        if mapId not in SAVED_MAPS:
            response = Response(
                {
                    "status": "error",
                    "message": "Map not found!"
                }, status=status.HTTP_400_BAD_REQUEST)
            return response
        roadsUpdate = request.data.get('roads')
        map = Map(mapId, SAVED_MAPS[mapId])
        for road in map.roads:
            target = roadsUpdate[road.id_]
            SAVED_MAPS[mapId]["roads"][road.id_]["lanesCarNumbers"] = target["lanesCarNumbers"]

        response = Response({
            "status": "ok",
            "message": "Roads updated!"
        }, status=status.HTTP_200_OK)
        return response


class IsConnectedViewSet(generics.GenericAPIView):
    def get(self, request):
        response = Response({
            "status": "ok",
            "message": "Connection established!"
        }, status=status.HTTP_200_OK)
        return response
