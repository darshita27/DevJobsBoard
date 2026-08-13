import io
import os
import secrets

from django.core.management import call_command
from django.db.models import Q
from django_filters.rest_framework import CharFilter, FilterSet
from rest_framework import mixins, permissions, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Favorite, Job
from .serializers import CategorySerializer, FavoriteSerializer, JobDetailSerializer, JobListSerializer

# key -> (min years, max years or None for "and above")
EXPERIENCE_BUCKETS = {
    'fresher': (0, 1),
    'junior': (1, 3),
    'mid': (3, 6),
    'senior': (6, 10),
    'lead': (10, None),
}


class JobFilter(FilterSet):
    category = CharFilter(field_name='category__slug')
    city = CharFilter(field_name='city', lookup_expr='iexact')
    work_mode = CharFilter(field_name='work_mode')
    experience = CharFilter(method='filter_experience')

    class Meta:
        model = Job
        fields = ['category', 'city', 'work_mode', 'experience']

    def filter_experience(self, queryset, name, value):
        bucket = EXPERIENCE_BUCKETS.get(value)
        if not bucket:
            return queryset

        low, high = bucket
        qs = queryset.exclude(min_experience_years__isnull=True)
        if high is not None:
            qs = qs.filter(min_experience_years__lte=high)
        return qs.filter(Q(max_experience_years__gte=low) | Q(max_experience_years__isnull=True))


class JobViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Job.objects.filter(is_active=True).select_related('category').prefetch_related('skills')
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    filterset_class = JobFilter
    search_fields = ['title', 'company', 'description']
    ordering_fields = ['posted_date', 'created_at', 'deadline']

    def get_serializer_class(self):
        return JobDetailSerializer if self.action == 'retrieve' else JobListSerializer


class CategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']
    pagination_class = None

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related('job', 'job__category')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        if instance.user_id != self.request.user.id:
            raise PermissionDenied('Not your favorite.')
        instance.delete()


class FetchJobsTriggerView(APIView):
    """Runs the fetch_jobs command on request. Auth is a shared-secret header, not a user
    account, so this can be called by an external scheduler (cron-job.org, GitHub Actions, ...)."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        expected = os.environ.get('FETCH_JOBS_TOKEN')
        provided = request.headers.get('X-Fetch-Token', '')
        if not expected or not secrets.compare_digest(provided, expected):
            return Response({'detail': 'Forbidden.'}, status=403)

        buf = io.StringIO()
        try:
            call_command('fetch_jobs', stdout=buf, stderr=buf)
        except Exception as err:  # noqa: BLE001
            return Response({'detail': f'fetch_jobs failed: {err}', 'output': buf.getvalue()}, status=500)
        return Response({'detail': 'ok', 'output': buf.getvalue()})
