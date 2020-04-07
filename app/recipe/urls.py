from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipe.views import TagViewSet, IngredientViewSet


app_name = 'recipe'

router = DefaultRouter()
router.register('tag', TagViewSet)
router.register('ingredient', IngredientViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
