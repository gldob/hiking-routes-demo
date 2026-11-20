from django.urls import path

from routes import views

urlpatterns = [
    path("routes/", views.route_collection),
    path("routes/<int:route_id>/", views.route_detail),
]
