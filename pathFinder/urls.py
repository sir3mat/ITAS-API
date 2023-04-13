from django.urls import path

from pathFinder import views


urlpatterns = [
    path("", views.PathFinderViewSet.as_view(), name="index"),
]
