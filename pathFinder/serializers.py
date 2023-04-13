from rest_framework import generics
from rest_framework import serializers


class GetPathsSerializer(serializers.Serializer):
    mapId = serializers.IntegerField()
    fromIntersection = serializers.IntegerField()
    toIntersection = serializers.IntegerField()


class PathResponseSerializer(serializers.Serializer):
    pathId = serializers.IntegerField()
    path = serializers.ListField(child=serializers.StringRelatedField())


class ErrorResponseSerializer(serializers.Serializer):
    error = serializers.StringRelatedField()
