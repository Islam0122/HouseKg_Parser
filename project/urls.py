from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # API v1
    path("api/v1/", include("apps.parser_functions.urls")),
    path("api/v1/users/", include("apps.user.urls")),

    # Swagger / OpenAPI
    path("api/schema/",         SpectacularAPIView.as_view(),        name="schema"),
    path("api/docs/",           SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/docs/redoc/",     SpectacularRedocView.as_view(url_name="schema"),   name="redoc"),
]