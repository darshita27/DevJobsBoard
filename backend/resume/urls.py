from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import TailorResumeView, TailoredResumeViewSet

router = DefaultRouter()
router.register('tailored-resumes', TailoredResumeViewSet, basename='tailored-resume')

urlpatterns = [
    path('tailor-resume/', TailorResumeView.as_view(), name='tailor-resume'),
] + router.urls
