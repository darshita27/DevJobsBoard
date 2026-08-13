from rest_framework import serializers

from .models import Category, Favorite, Job, Skill


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']


class JobListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Job
        fields = [
            'id', 'slug', 'title', 'company', 'location', 'city', 'work_mode',
            'category', 'salary_text', 'experience_text', 'deadline', 'posted_date',
        ]


class JobDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            'id', 'slug', 'title', 'company', 'location', 'city', 'work_mode',
            'category', 'skills', 'experience_text', 'salary_text', 'eligibility',
            'description', 'deadline', 'apply_url', 'posted_date', 'source',
            'is_active', 'is_favorited',
        ]

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.favorited_by.filter(user=request.user).exists()


class FavoriteSerializer(serializers.ModelSerializer):
    job = JobListSerializer(read_only=True)
    job_id = serializers.PrimaryKeyRelatedField(
        queryset=Job.objects.filter(is_active=True), source='job', write_only=True,
    )

    class Meta:
        model = Favorite
        fields = ['id', 'job', 'job_id', 'created_at']
