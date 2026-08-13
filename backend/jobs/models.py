from django.conf import settings
from django.db import models
from slugify import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=80, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Job(models.Model):
    class WorkMode(models.TextChoices):
        REMOTE = 'remote', 'Remote'
        ONSITE = 'onsite', 'On-site'
        HYBRID = 'hybrid', 'Hybrid'
        UNSPECIFIED = 'unspecified', 'Not specified'

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    fingerprint = models.CharField(max_length=40, unique=True, null=True, blank=True, db_index=True)
    company = models.CharField(max_length=150, db_index=True)
    location = models.CharField(max_length=150, blank=True)
    city = models.CharField(max_length=100, blank=True, db_index=True)
    work_mode = models.CharField(max_length=20, choices=WorkMode.choices, default=WorkMode.UNSPECIFIED)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='jobs')
    skills = models.ManyToManyField(Skill, blank=True, related_name='jobs')
    experience_text = models.CharField(max_length=100, blank=True, default='Not specified')
    min_experience_years = models.PositiveSmallIntegerField(null=True, blank=True)
    max_experience_years = models.PositiveSmallIntegerField(null=True, blank=True)
    salary_text = models.CharField(max_length=150, blank=True, default='Not disclosed')
    eligibility = models.TextField(blank=True)
    description = models.TextField(blank=True)
    deadline = models.DateField(null=True, blank=True)
    apply_url = models.URLField(max_length=500)
    posted_date = models.DateField(null=True, blank=True)
    source = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-posted_date', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(f'{self.company}-{self.title}')[:240]
            slug, n = base, 2
            while Job.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{n}'
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.title} @ {self.company}'


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} → {self.job}'
