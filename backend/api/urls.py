from api.views import (IngredientViewSet, RecipeViewSet, TagViewSet,
                       UsersViewSet)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

v1_router = DefaultRouter()
v1_router.register("tags", TagViewSet, "tags")
v1_router.register("ingredients", IngredientViewSet, "ingredients")
v1_router.register("recipes", RecipeViewSet, "recipes")
v1_router.register("users", UsersViewSet, basename="users")

urlpatterns = (
    path("", include(v1_router.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
)
