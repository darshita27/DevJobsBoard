from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, FavoriteViewSet, JobViewSet

router = DefaultRouter()
router.register('jobs', JobViewSet, basename='job')
router.register('categories', CategoryViewSet, basename='category')
router.register('favorites', FavoriteViewSet, basename='favorite')

urlpatterns = router.urls
