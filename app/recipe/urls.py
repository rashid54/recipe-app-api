from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipe.views import TagViewSet, IngredientViewSet, RecipeViewSet


app_name = 'recipe'

router = DefaultRouter()
router.register('tag', TagViewSet)
router.register('ingredient', IngredientViewSet)
router.register('recipe', RecipeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
