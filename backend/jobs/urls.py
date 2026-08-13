from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, FavoriteViewSet, FetchJobsTriggerView, JobViewSet

router = DefaultRouter()
router.register('jobs', JobViewSet, basename='job')
router.register('categories', CategoryViewSet, basename='category')
router.register('favorites', FavoriteViewSet, basename='favorite')

urlpatterns = [
    path('internal/fetch-jobs/', FetchJobsTriggerView.as_view(), name='fetch-jobs-trigger'),
] + router.urls
