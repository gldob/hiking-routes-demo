from django.urls import include, path

from hiking.views import health

urlpatterns = [
    path("health/", health),
    path("api/", include("routes.urls")),
]

handler404 = "hiking.views.not_found"
handler500 = "hiking.views.server_error"
