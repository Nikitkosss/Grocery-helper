from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (BaseAPIRootView, IngredientViewSet, RecipeViewSet,
                       TagViewSet, UserViewSet)

app_name = "api"


class RuDefaultRouter(DefaultRouter):
    APIRootView = BaseAPIRootView


router = RuDefaultRouter()
router.register("tags", TagViewSet, "tags")
router.register("ingredients", IngredientViewSet, "ingredients")
router.register("recipes", RecipeViewSet, "recipes")
router.register("users", UserViewSet, "users")

urlpatterns = (
    path("", include(router.urls)),
    path("auth/", include("djoser.urls.authtoken")),
)
