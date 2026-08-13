from django.conf import settings
from django.db import models


class TailoredResume(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tailored_resumes')
    job = models.ForeignKey('jobs.Job', on_delete=models.SET_NULL, null=True, blank=True, related_name='tailored_resumes')
    job_title = models.CharField(max_length=200, blank=True)
    company = models.CharField(max_length=150, blank=True)
    job_description_snapshot = models.TextField()
    original_resume = models.TextField()
    tailored_resume = models.TextField()
    summary_of_changes = models.JSONField(default=list, blank=True)
    matched_keywords = models.JSONField(default=list, blank=True)
    ats_tips = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} → {self.job_title or "custom JD"} ({self.created_at:%Y-%m-%d})'
