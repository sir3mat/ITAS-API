from django.urls import path

from pathFinder import views

urlpatterns = [
    path("pathFinder", views.PathFinderViewSet.as_view(), name="pathFinder"),
    path("newMap", views.NewMapViewSet.as_view(), name="newMap"),
]
