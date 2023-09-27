class RecipeViewSet(viewsets.ModelViewSet): 
     """Вьюсет рецепта. 
        Просмотр, создание, редактирование.""" 
     queryset = Recipe.objects.all() 
     permission_classes = [IsOwnerOrReadOnly | IsAmdinOrReadOnly] 
     pagination_class = RecipePagination 
     filter_backends = (DjangoFilterBackend,) 
     filterset_class = RecipeFilter 
  
     def perform_create(self, serializer): 
         serializer.save(author=self.request.user) 
  
     def get_serializer_class(self): 
         if self.request.method in SAFE_METHODS: 
             return RecipeReadSerializer 
         return RecipeCreateSerializer 
  
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
             fav_rec = request.user.favorites.filter(recipe_id=pk) 
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
             rec_in_cart = request.user.shopping_cart.filter(recipe_id=pk) 
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
         methods=['get'], 
         permission_classes=(IsAuthenticated,)) 
     def download_shopping_cart(self, request): 
         user = request.user 
         buffer = io.BytesIO() 
         ingredients = IngredientAmount.objects.filter( 
             reciperecipe_shopping_cartuser=user).values( 
                 'ingredientname', 'ingredientmeasurement_unit').annotate( 
                 amount=Sum('amount')) 
         shopping_list = ([f'{i["ingredient__name"]}' 
                           f' - {i["amount"]}' 
                           f' ({i["ingredient__measurement_unit"]}' 
                           for i in ingredients]) 
         text = canvas.Canvas(buffer) 
         font = ttfonts.TTFont('Arial', './docs/arialfont.ttf') 
         pdfmetrics.registerFont(font) 
         text.setFont('Arial', settings.HEAD_FONT_SIZE) 
         text.drawString(settings.HEAD_INDENT, settings.HEAD_HEIGHT, 
                         'Ваш список покупок:')

text.setFont('Arial', settings.TEXT_FONT_SIZE) 
         for line in shopping_list: 
             text.drawString(settings.TEXT_INDENT, settings.TEXT_HEIGHT, line) 
             settings.TEXT_HEIGHT -= settings.LINE_SPACE 
         text.showPage() 
         text.save() 
         buffer.seek(0) 
         return FileResponse(buffer, 
                             as_attachment=True, 
                             filename='shopping_cart.pdf')