from django.contrib import admin
from .models import Resume, Experience, Education, Skill, ContactMessage


class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 0


class EducationInline(admin.TabularInline):
    model = Education
    extra = 0


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 0


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ['title', 'full_name', 'user', 'email', 'template', 'created_at', 'updated_at']
    list_filter = ['template', 'created_at']
    search_fields = ['title', 'full_name', 'email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [ExperienceInline, EducationInline, SkillInline]


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ['job_title', 'company', 'resume', 'start_date', 'end_date']
    list_filter = ['start_date']
    search_fields = ['job_title', 'company']


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['degree', 'institution', 'resume', 'start_date']
    search_fields = ['degree', 'institution']


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'proficiency', 'resume']
    list_filter = ['category', 'proficiency']
    search_fields = ['name']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject']
