from django.urls import path

from pathFinder import views

urlpatterns = [
    path("pathFinder", views.PathFinderViewSet.as_view(), name="pathFinder"),
    path("map", views.MapViewSet.as_view(), name="map"),
    path("roads", views.RoadsViewSet.as_view(),
         name="roads"),
]
