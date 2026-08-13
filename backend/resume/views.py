from rest_framework import mixins, permissions, status, viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from jobs.models import Job

from .models import TailoredResume
from .serializers import TailorResumeRequestSerializer, TailoredResumeSerializer
from .services import ResumeTailorError, extract_text_from_upload, tailor_resume


class TailorResumeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = TailorResumeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        job = None
        job_title = ''
        company = ''
        job_description = (data.get('job_description') or '').strip()

        if data.get('job_slug'):
            job = Job.objects.filter(slug=data['job_slug'], is_active=True).first()
            if not job:
                return Response({'detail': 'Job not found.'}, status=status.HTTP_404_NOT_FOUND)
            job_title, company = job.title, job.company
            if not job_description:
                job_description = job.description

        resume_text = (data.get('resume_text') or '').strip()
        if not resume_text and data.get('resume_file'):
            try:
                resume_text = extract_text_from_upload(data['resume_file']).strip()
            except ValueError as err:
                return Response({'detail': str(err)}, status=status.HTTP_400_BAD_REQUEST)

        if not resume_text:
            return Response(
                {'detail': 'Could not extract any text from the resume.'}, status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = tailor_resume(
                resume_text=resume_text, job_description=job_description, job_title=job_title, company=company,
            )
        except ResumeTailorError as err:
            return Response({'detail': str(err)}, status=status.HTTP_502_BAD_GATEWAY)

        instance = TailoredResume.objects.create(
            user=request.user,
            job=job,
            job_title=job_title,
            company=company,
            job_description_snapshot=job_description,
            original_resume=resume_text,
            tailored_resume=result['tailored_resume'],
            summary_of_changes=result['summary_of_changes'],
            matched_keywords=result['matched_keywords'],
            ats_tips=result['ats_tips'],
        )
        return Response(TailoredResumeSerializer(instance).data, status=status.HTTP_201_CREATED)


class TailoredResumeViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet,
):
    serializer_class = TailoredResumeSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return TailoredResume.objects.filter(user=self.request.user).select_related('job')
