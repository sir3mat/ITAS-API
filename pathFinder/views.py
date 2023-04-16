from rest_framework import status
from rest_framework.response import Response
from .types import CarReq
from rest_framework import generics
from .services import PathFinderService
from drf_spectacular.utils import extend_schema
from .serializers import GetPathsSerializer, PathResponseSerializer, ErrorResponseSerializer


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
        mapId = int(request.query_params["mapId"])
        fromIntersection = int(request.query_params["fromIntersection"])
        toIntersection = int(request.query_params["toIntersection"])
        pathFinder_service = PathFinderService()
        req = CarReq(mapId, fromIntersection, toIntersection)
        res = pathFinder_service.getPath(req)
        if res is None:
            response = Response(
                {"error": "End node could not be reached!"}, status=status.HTTP_400_BAD_REQUEST)
            return response

        response = Response(res, status=status.HTTP_200_OK)
        return response
