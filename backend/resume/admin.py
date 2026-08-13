from django.contrib import admin

from .models import TailoredResume


@admin.register(TailoredResume)
class TailoredResumeAdmin(admin.ModelAdmin):
    list_display = ('user', 'job_title', 'company', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'job_title', 'company')
