from api.filters import IngredientFilter, RecipeFilter
from api.permissions import AuthorOrReadOnly
from api.serializers import (CreateUpdateRecipeSerializer,
                             IngredientSerializer, RecipeSerializer,
                             SubscribeSerializer, TagSerializer,
                             UsersSerializer, FavoriteSerializer,
                             ShoppingCartSerializer, SubscribeCreateSerializer)
from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import Subscribe, User


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filterset_class = IngredientFilter
    filter_backends = (DjangoFilterBackend,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AuthorOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        return Recipe.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return CreateUpdateRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

    @staticmethod
    def create_obj(request, pk, serializers):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        data = {'user': user.id,
                'recipe': recipe.pk}
        serializer = serializers(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.create_obj(
                request=request,
                pk=pk,
                serializers=FavoriteSerializer)

        if request.method == 'DELETE':
            fav_rec = Favorite.objects.filter(recipe_id=pk)
            if fav_rec.exists():
                fav_rec.delete()
                return Response(
                    {'message': 'Рецепт удален из избранного'},
                    status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Рецепт уже удален!'},
                status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        pagination_class=None
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.create_obj(
                request=request,
                pk=pk,
                serializers=ShoppingCartSerializer)
        if request.method == 'DELETE':
            rec_in_cart = ShoppingCart.objects.filter(recipe_id=pk)
            if rec_in_cart.exists():
                rec_in_cart.delete()
                return Response(
                    {'message': 'Рецепт удален из списка покупок'},
                    status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Рецепт уже удален из списка покупок!'},
                status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=('GET',),
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = IngredientAmount.objects.filter(
            recipe__shopping_cart__user=user).values(
            'ingredient__name',
            'ingredient__measurement_unit').annotate(
            amount=Sum('amount')
        )
        data = []
        for ingredient in ingredients:
            data.append(
                f'{ingredient["ingredient__name"]} - '
                f'{ingredient["amount"]} '
                f'{ingredient["ingredient__measurement_unit"]}'
            )
        content = 'Список покупок:\n\n' + '\n'.join(data)
        filename = 'shopping_list.txt'
        request = HttpResponse(content, content_type='text/plain')
        request['Content-Disposition'] = f'attachment; filename={filename}'
        return request


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (AllowAny,)
    pagination_class = PageNumberPagination

    @action(
        detail=False,
        methods=('GET', 'PUT',),
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        self.object = get_object_or_404(User, pk=request.user.id)
        serializer = self.get_serializer(self.object)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated, ],
        url_path='subscribe'
    )
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        user = request.user
        if request.method == 'POST':
            serializer = SubscribeCreateSerializer(
                data={
                    'user': user.id,
                    'author': author.id
                },
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription = Subscribe.objects.filter(user=user, author=author)
            if subscription.exists():
                subscription.delete()
                return Response(
                    {'message': 'Вы больше не подписаны на пользователя'},
                    status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Вы не подписаны на этого пользователя!'},
                status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        serializer = SubscribeSerializer(
            self.paginate_queryset(
                User.objects.filter(author__user=request.user)
            ),
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
