from django.urls import path

from pathFinder import views

urlpatterns = [
    # path("", views.IndexViewSet.as_view(), name="index"),
    path('', views.api_urls, name='api_urls'),

    # API endpoints
    path("pathFinder", views.PathFinderViewSet.as_view(), name="pathFinder"),
    path("map", views.MapViewSet.as_view(), name="map"),
    path("roads", views.RoadsViewSet.as_view(), name="roads"),
    path("onlinePathFinder", views.OnlinePathFinderViewSet.as_view(), name="onlinePathFinder"),
    # Connection to the frontend
    path("isConnected", views.IsConnectedViewSet.as_view(), name="isConnected"),
]
