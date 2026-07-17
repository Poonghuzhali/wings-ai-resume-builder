from django.db import models
from django.contrib.auth.models import User
import uuid


class Resume(models.Model):
    TEMPLATE_CHOICES = [
        ('modern', 'Modern'),
        ('classic', 'Classic'),
        ('creative', 'Creative'),
        ('minimal', 'Minimal'),
        ('executive', 'Executive'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, default='My Resume')
    template = models.CharField(max_length=20, choices=TEMPLATE_CHOICES, default='modern')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Personal Info
    full_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=200, blank=True)
    linkedin_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    professional_summary = models.TextField(blank=True)

    # AI Generated Content
    ai_summary = models.TextField(blank=True)
    ai_skills = models.TextField(blank=True)
    ai_experience_bullets = models.TextField(blank=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} - {self.full_name}"


class Experience(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='experiences')
    job_title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', '-start_date']

    def __str__(self):
        return f"{self.job_title} at {self.company}"


class Education(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='educations')
    degree = models.CharField(max_length=200)
    institution = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    gpa = models.CharField(max_length=10, blank=True)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', '-start_date']

    def __str__(self):
        return f"{self.degree} - {self.institution}"


class Skill(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100, blank=True, default='Technical')
    proficiency = models.IntegerField(default=3, choices=[(i, i) for i in range(1, 6)])

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return self.name


class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=300)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"
