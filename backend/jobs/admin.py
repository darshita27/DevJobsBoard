from django.contrib import admin

from .models import Category, Favorite, Job, Skill


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'company', 'city', 'work_mode', 'category',
        'min_experience_years', 'max_experience_years', 'is_active', 'posted_date',
    ]
    list_filter = ['work_mode', 'category', 'is_active']
    search_fields = ['title', 'company', 'city']
    prepopulated_fields = {'slug': ('company', 'title')}
    filter_horizontal = ['skills']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'job', 'created_at']
