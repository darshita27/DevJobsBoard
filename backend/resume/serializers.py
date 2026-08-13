from rest_framework import serializers

from .models import TailoredResume


class TailorResumeRequestSerializer(serializers.Serializer):
    job_slug = serializers.SlugField(required=False, allow_blank=True)
    job_description = serializers.CharField(required=False, allow_blank=True)
    resume_text = serializers.CharField(required=False, allow_blank=True)
    resume_file = serializers.FileField(required=False)

    def validate(self, attrs):
        if not attrs.get('job_slug') and not (attrs.get('job_description') or '').strip():
            raise serializers.ValidationError('Select a job or paste a job description.')
        if not (attrs.get('resume_text') or '').strip() and not attrs.get('resume_file'):
            raise serializers.ValidationError('Paste your resume text or upload a resume file.')
        return attrs


class TailoredResumeSerializer(serializers.ModelSerializer):
    job_slug = serializers.SlugField(source='job.slug', read_only=True, default=None)

    class Meta:
        model = TailoredResume
        fields = [
            'id', 'job_slug', 'job_title', 'company', 'tailored_resume',
            'summary_of_changes', 'matched_keywords', 'ats_tips', 'created_at',
        ]
