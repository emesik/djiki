from django.urls import include, path

urlpatterns = [
    path("djiki/", include("djiki.urls")),
]
