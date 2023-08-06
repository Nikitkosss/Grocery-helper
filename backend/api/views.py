from django.contrib.auth import get_user_model
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q, QuerySet
from django.http.response import HttpResponse
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.response import Response
from rest_framework.routers import APIRootView
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.enums import Tuples, UrlQueries
from api.mixins import AddDelViewMixin
from api.paginators import PageLimitPagination
from api.permissions import AdminOrReadOnly, AuthorStaffOrReadOnly
from api.serializers import (IngredientSerializer, RecipeSerializer,
                             TagSerializer, UserSubscribeSerializer)
from api.services import create_shoping_list
from recipes.models import Carts, Favorites, Ingredient, Recipe, Tag
from users.models import Subscriptions

User = get_user_model()


class BaseAPIRootView(APIRootView):
    """Базовые пути API приложения"""


class UserViewSet(DjoserUserViewSet, AddDelViewMixin):

    pagination_class = PageLimitPagination
    permission_classes = (DjangoModelPermissions,)
    add_serializer = UserSubscribeSerializer
    link_model = Subscriptions

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def subscribe(self, request: WSGIRequest, id) -> Response:
        """Создаёт/удалет связь между пользователями"""

    @subscribe.mapping.post
    def create_subscribe(
        self, request: WSGIRequest, id
    ) -> Response:
        return self._create_relation(id)

    @subscribe.mapping.delete
    def delete_subscribe(
        self, request: WSGIRequest, id
    ) -> Response:
        return self._delete_relation(Q(author__id=id))

    @action(
        methods=("get",), detail=False, permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request: WSGIRequest) -> Response:
        pages = self.paginate_queryset(
            User.objects.filter(subscribers__user=self.request.user)
        )
        serializer = UserSubscribeSerializer(pages, many=True)
        return self.get_paginated_response(serializer.data)


class TagViewSet(ReadOnlyModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)


class IngredientViewSet(ReadOnlyModelViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)

    def get_queryset(self) -> list[Ingredient]:
        name: str = self.request.query_params.get(UrlQueries.SEARCH_ING_NAME)
        queryset = self.queryset

        if not name:
            return queryset

        start_queryset = queryset.filter(name__istartswith=name)
        start_names = (ing.name for ing in start_queryset)
        contain_queryset = queryset.filter(name__icontains=name).exclude(
            name__in=start_names
        )
        return list(start_queryset) + list(contain_queryset)


class RecipeViewSet(ModelViewSet, AddDelViewMixin):

    queryset = Recipe.objects.select_related("author")
    serializer_class = RecipeSerializer
    permission_classes = (AuthorStaffOrReadOnly,)
    pagination_class = PageLimitPagination
    add_serializer = RecipeSerializer

    def get_queryset(self) -> QuerySet[Recipe]:
        queryset = self.queryset

        tags: list = self.request.query_params.getlist(UrlQueries.TAGS.value)
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        author: str = self.request.query_params.get(UrlQueries.AUTHOR.value)
        if author:
            queryset = queryset.filter(author=author)

        # Следующие фильтры только для авторизованного пользователя
        if self.request.user.is_anonymous:
            return queryset

        is_in_cart: str = self.request.query_params.get(UrlQueries.SHOP_CART)
        if is_in_cart in Tuples.SYMBOL_TRUE_SEARCH.value:
            queryset = queryset.filter(in_carts__user=self.request.user)
        elif is_in_cart in Tuples.SYMBOL_FALSE_SEARCH.value:
            queryset = queryset.exclude(in_carts__user=self.request.user)

        is_favorite: str = self.request.query_params.get(UrlQueries.FAVORITE)
        if is_favorite in Tuples.SYMBOL_TRUE_SEARCH.value:
            queryset = queryset.filter(in_favorites__user=self.request.user)
        if is_favorite in Tuples.SYMBOL_FALSE_SEARCH.value:
            queryset = queryset.exclude(in_favorites__user=self.request.user)

        return queryset

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        """Добавляет/удалет рецепт в `избранное`"""

    @favorite.mapping.post
    def recipe_to_favorites(
        self, request, pk
    ):
        self.link_model = Favorites
        return self._create_relation(pk)

    @favorite.mapping.delete
    def remove_recipe_from_favorites(
        self, request, pk
    ):
        self.link_model = Favorites
        return self._delete_relation(Q(recipe__id=pk))

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        """Добавляет/удалет рецепт в `список покупок`"""

    @shopping_cart.mapping.post
    def recipe_to_cart(self, request, pk):
        self.link_model = Carts
        return self._create_relation(pk)

    @shopping_cart.mapping.delete
    def remove_recipe_from_cart(
        self, request, pk
    ):
        self.link_model = Carts
        return self._delete_relation(Q(recipe__id=pk))

    @action(methods=("get",), detail=False)
    def download_shopping_cart(self, request):
        """Загружает файл *.txt со списком покупок"""
        user = self.request.user
        if not user.carts.exists():
            return Response(status=HTTP_400_BAD_REQUEST)

        filename = f"{user.username}_shopping_list.txt"
        shopping_list = create_shoping_list(user)
        response = HttpResponse(
            shopping_list, content_type="text.txt; charset=utf-8"
        )
        response["Content-Disposition"] = f"attachment; filename={filename}"
        return response
