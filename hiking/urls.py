from django.urls import path

from hiking.views import health

urlpatterns = [
    path("health/", health),
]

handler404 = "hiking.views.not_found"
handler500 = "hiking.views.server_error"
