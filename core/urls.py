from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Public
    path('advice/', views.advice_view, name='advice'),
    path('contact/', views.contact_view, name='contact'),

    # Resumes
    path('resumes/', views.my_resumes, name='my_resumes'),
    path('create/', views.create_resume, name='create_resume'),
    path('resume/<uuid:resume_id>/', views.edit_resume, name='edit_resume'),
    path('resume/<uuid:resume_id>/preview/', views.preview_resume, name='preview_resume'),
    path('resume/<uuid:resume_id>/delete/', views.delete_resume, name='delete_resume'),
    path('resume/<uuid:resume_id>/download/', views.download_resume, name='download_resume'),

    # Experience
    path('resume/<uuid:resume_id>/experience/add/', views.add_experience, name='add_experience'),
    path('resume/<uuid:resume_id>/experience/<int:exp_id>/delete/', views.delete_experience, name='delete_experience'),

    # Education
    path('resume/<uuid:resume_id>/education/add/', views.add_education, name='add_education'),
    path('resume/<uuid:resume_id>/education/<int:edu_id>/delete/', views.delete_education, name='delete_education'),

    # Skills
    path('resume/<uuid:resume_id>/skill/add/', views.add_skill, name='add_skill'),
    path('resume/<uuid:resume_id>/skill/<int:skill_id>/delete/', views.delete_skill, name='delete_skill'),

    # AI Endpoints
    path('resume/<uuid:resume_id>/ai/summary/', views.ai_generate_summary, name='ai_generate_summary'),
    path('resume/<uuid:resume_id>/ai/bullets/', views.ai_generate_bullets, name='ai_generate_bullets'),
    path('resume/<uuid:resume_id>/ai/skills/', views.ai_suggest_skills, name='ai_suggest_skills'),
    path('resume/<uuid:resume_id>/ai/optimize/', views.ai_optimize, name='ai_optimize'),
]
