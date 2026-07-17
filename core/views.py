from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count
from .models import Resume, Experience, Education, Skill, ContactMessage
from .openai_service import (
    generate_professional_summary,
    generate_experience_bullets,
    generate_skills_suggestions,
    optimize_resume_content,
)
import json
import re


# ─── AUTH ────────────────────────────────────────────────────────
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        errors = []
        if not username:
            errors.append('Username is required.')
        elif len(username) < 3:
            errors.append('Username must be at least 3 characters.')
        elif not re.match(r'^[a-zA-Z0-9_]+$', username):
            errors.append('Username can only contain letters, numbers, and underscores.')
        elif User.objects.filter(username=username).exists():
            errors.append('Username already taken.')

        if not email:
            errors.append('Email is required.')
        elif not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            errors.append('Enter a valid email address.')
        elif User.objects.filter(email=email).exists():
            errors.append('Email already registered.')

        if not first_name:
            errors.append('First name is required.')

        if not password:
            errors.append('Password is required.')
        elif len(password) < 8:
            errors.append('Password must be at least 8 characters.')
        elif password.isdigit():
            errors.append('Password cannot be entirely numeric.')

        if password != password2:
            errors.append('Passwords do not match.')

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'core/register.html', {
                'form_data': request.POST,
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        login(request, user)
        messages.success(request, f'Welcome to Wings AI, {first_name}!')
        return redirect('home')

    return render(request, 'core/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        remember = request.POST.get('remember')

        if not username or not password:
            messages.error(request, 'Please enter both username and password.')
            return render(request, 'core/login.html', {'form_data': request.POST})

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if not remember:
                request.session.set_expiry(0)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'core/login.html', {'form_data': request.POST})

    return render(request, 'core/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


# ─── PUBLIC PAGES ────────────────────────────────────────────────
def home(request):
    user_resumes = []
    if request.user.is_authenticated:
        user_resumes = Resume.objects.filter(user=request.user)[:6]
    return render(request, 'core/home.html', {'user_resumes': user_resumes})


def advice_view(request):
    tips = [
        {
            'title': 'Tailor Your Resume for Each Job',
            'icon': 'fa-crosshairs',
            'color': 'green',
            'content': 'Read the job description carefully and mirror the keywords and skills they mention. ATS systems scan for exact keyword matches, so customizing your resume for each application dramatically increases your chances.',
        },
        {
            'title': 'Start Bullets with Strong Action Verbs',
            'icon': 'fa-bolt',
            'color': 'gold',
            'content': 'Begin each bullet point with powerful action verbs like "Spearheaded", "Architected", "Optimized", "Delivered". Avoid weak phrases like "Responsible for" or "Helped with". Strong verbs show initiative and impact.',
        },
        {
            'title': 'Quantify Your Achievements',
            'icon': 'fa-chart-line',
            'color': 'teal',
            'content': 'Numbers speak louder than words. Instead of "Improved performance", write "Improved API response time by 40%, reducing server costs by $12K annually". Concrete metrics make your achievements tangible and memorable.',
        },
        {
            'title': 'Keep It to One or Two Pages',
            'icon': 'fa-file-alt',
            'color': 'sage',
            'content': 'For most professionals, a one-page resume is ideal. Senior professionals with 10+ years of experience can go to two pages. Every line should earn its place — if it does not add value, remove it.',
        },
        {
            'title': 'Use a Clean, ATS-Friendly Format',
            'icon': 'fa-paint-brush',
            'color': 'mint',
            'content': 'Avoid tables, columns, headers/footers, and unusual fonts. Stick to standard section headings (Experience, Education, Skills). Use a clean font like Inter, Calibri, or Arial at 10-12pt size.',
        },
        {
            'title': 'Write a Compelling Summary',
            'icon': 'fa-star',
            'color': 'olive',
            'content': 'Your professional summary is the first thing recruiters read. In 3-4 lines, highlight your years of experience, key skills, notable achievements, and what you bring to the role. Make it specific, not generic.',
        },
        {
            'title': 'Include Relevant Keywords',
            'icon': 'fa-key',
            'color': 'green',
            'content': 'Most companies use ATS software to filter resumes. Research the top skills and tools in your industry and ensure they appear naturally in your resume. Our AI assistant can suggest the best keywords for your target role.',
        },
        {
            'title': 'Proofread Relentlessly',
            'icon': 'fa-check-circle',
            'color': 'gold',
            'content': 'A single typo can send your resume to the rejection pile. Read it aloud, use grammar tools, and have a friend review it. Pay special attention to names, dates, and contact information.',
        },
    ]
    return render(request, 'core/advice.html', {'tips': tips})


def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message_text = request.POST.get('message', '').strip()

        errors = []
        if not name:
            errors.append('Name is required.')
        if not email or not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            errors.append('Valid email is required.')
        if not subject:
            errors.append('Subject is required.')
        if not message_text:
            errors.append('Message is required.')

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'core/contact.html', {
                'form_data': request.POST,
            })

        ContactMessage.objects.create(
            name=name, email=email, subject=subject, message=message_text,
        )
        messages.success(request, 'Your message has been sent! We will get back to you soon.')
        return redirect('contact')

    return render(request, 'core/contact.html')


# ─── RESUME CRUD (login required) ───────────────────────────────
@login_required(login_url='login')
def my_resumes(request):
    resumes = Resume.objects.filter(user=request.user)
    return render(request, 'core/my_resumes.html', {'resumes': resumes})


@login_required(login_url='login')
def create_resume(request):
    if request.method == 'POST':
        resume = Resume.objects.create(
            user=request.user,
            title=request.POST.get('title', 'My Resume'),
            template=request.POST.get('template', 'modern'),
            full_name=request.POST.get('full_name', ''),
            email=request.POST.get('email', ''),
            phone=request.POST.get('phone', ''),
            location=request.POST.get('location', ''),
            linkedin_url=request.POST.get('linkedin_url', ''),
            portfolio_url=request.POST.get('portfolio_url', ''),
            professional_summary=request.POST.get('professional_summary', ''),
        )
        messages.success(request, 'Resume created successfully!')
        return redirect('edit_resume', resume_id=resume.id)
    return render(request, 'core/create_resume.html')


@login_required(login_url='login')
def edit_resume(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    experiences = resume.experiences.all()
    educations = resume.educations.all()
    skills = resume.skills.all()

    if request.method == 'POST':
        resume.full_name = request.POST.get('full_name', resume.full_name)
        resume.email = request.POST.get('email', resume.email)
        resume.phone = request.POST.get('phone', resume.phone)
        resume.location = request.POST.get('location', resume.location)
        resume.linkedin_url = request.POST.get('linkedin_url', resume.linkedin_url)
        resume.portfolio_url = request.POST.get('portfolio_url', resume.portfolio_url)
        resume.professional_summary = request.POST.get('professional_summary', resume.professional_summary)
        resume.title = request.POST.get('title', resume.title)
        resume.template = request.POST.get('template', resume.template)
        resume.save()
        messages.success(request, 'Resume updated successfully!')
        return redirect('edit_resume', resume_id=resume.id)

    return render(request, 'core/edit_resume.html', {
        'resume': resume, 'experiences': experiences,
        'educations': educations, 'skills': skills,
    })


@login_required(login_url='login')
def preview_resume(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    return render(request, 'core/preview_resume.html', {
        'resume': resume,
        'experiences': resume.experiences.all(),
        'educations': resume.educations.all(),
        'skills': resume.skills.all(),
    })


@login_required(login_url='login')
def delete_resume(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    resume.delete()
    messages.success(request, 'Resume deleted successfully!')
    return redirect('my_resumes')


@login_required(login_url='login')
def download_resume(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    experiences = resume.experiences.all()
    educations = resume.educations.all()
    skills = resume.skills.all()

    html_string = render(request, 'core/pdf_template.html', {
        'resume': resume, 'experiences': experiences,
        'educations': educations, 'skills': skills,
    }).content.decode('utf-8')

    from io import BytesIO
    from xhtml2pdf import pisa

    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html_string, dest=pdf_buffer)
    if pisa_status.err:
        from django.http import HttpResponseServerError
        return HttpResponseServerError('Error generating PDF')

    pdf_buffer.seek(0)
    from django.http import HttpResponse
    response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{resume.full_name or resume.title}_resume.pdf"'
    return response


# ─── EXPERIENCE / EDUCATION / SKILL CRUD ────────────────────────
@login_required(login_url='login')
@csrf_exempt
@require_POST
def add_experience(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    data = json.loads(request.body) if request.content_type == 'application/json' else request.POST

    experience = Experience.objects.create(
        resume=resume,
        job_title=data.get('job_title', ''),
        company=data.get('company', ''),
        location=data.get('location', ''),
        start_date=data.get('start_date'),
        end_date=data.get('end_date') or None,
        is_current=data.get('is_current', 'false') in ('true', 'True', 'on', '1', True),
        description=data.get('description', ''),
        order=resume.experiences.count(),
    )
    if request.content_type == 'application/json':
        return JsonResponse({'id': str(experience.id), 'success': True})
    messages.success(request, 'Experience added!')
    return redirect('edit_resume', resume_id=resume.id)


@login_required(login_url='login')
@csrf_exempt
@require_POST
def delete_experience(request, resume_id, exp_id):
    experience = get_object_or_404(Experience, id=exp_id, resume__id=resume_id, resume__user=request.user)
    experience.delete()
    if request.content_type == 'application/json':
        return JsonResponse({'success': True})
    messages.success(request, 'Experience removed!')
    return redirect('edit_resume', resume_id=resume_id)


@login_required(login_url='login')
@csrf_exempt
@require_POST
def add_education(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    data = json.loads(request.body) if request.content_type == 'application/json' else request.POST

    education = Education.objects.create(
        resume=resume,
        degree=data.get('degree', ''),
        institution=data.get('institution', ''),
        location=data.get('location', ''),
        start_date=data.get('start_date'),
        end_date=data.get('end_date') or None,
        gpa=data.get('gpa', ''),
        description=data.get('description', ''),
        order=resume.educations.count(),
    )
    if request.content_type == 'application/json':
        return JsonResponse({'id': str(education.id), 'success': True})
    messages.success(request, 'Education added!')
    return redirect('edit_resume', resume_id=resume.id)


@login_required(login_url='login')
@csrf_exempt
@require_POST
def delete_education(request, resume_id, edu_id):
    education = get_object_or_404(Education, id=edu_id, resume__id=resume_id, resume__user=request.user)
    education.delete()
    if request.content_type == 'application/json':
        return JsonResponse({'success': True})
    messages.success(request, 'Education removed!')
    return redirect('edit_resume', resume_id=resume_id)


@login_required(login_url='login')
@csrf_exempt
@require_POST
def add_skill(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    data = json.loads(request.body) if request.content_type == 'application/json' else request.POST

    skill = Skill.objects.create(
        resume=resume,
        name=data.get('name', ''),
        category=data.get('category', 'Technical'),
        proficiency=int(data.get('proficiency', 3)),
    )
    if request.content_type == 'application/json':
        return JsonResponse({'id': str(skill.id), 'success': True})
    messages.success(request, 'Skill added!')
    return redirect('edit_resume', resume_id=resume.id)


@login_required(login_url='login')
@csrf_exempt
@require_POST
def delete_skill(request, resume_id, skill_id):
    skill = get_object_or_404(Skill, id=skill_id, resume__id=resume_id, resume__user=request.user)
    skill.delete()
    if request.content_type == 'application/json':
        return JsonResponse({'success': True})
    messages.success(request, 'Skill removed!')
    return redirect('edit_resume', resume_id=resume.id)


# ─── AI ENDPOINTS ───────────────────────────────────────────────
@login_required(login_url='login')
@csrf_exempt
@require_POST
def ai_generate_summary(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    try:
        data = json.loads(request.body)
        summary = generate_professional_summary(
            name=resume.full_name,
            job_title=data.get('job_title', ''),
            experience=data.get('experience', ''),
            skills=data.get('skills', ''),
        )
        resume.ai_summary = summary
        resume.save()
        return JsonResponse({'summary': summary, 'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e), 'success': False}, status=500)


@login_required(login_url='login')
@csrf_exempt
@require_POST
def ai_generate_bullets(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    try:
        data = json.loads(request.body)
        bullets = generate_experience_bullets(
            job_title=data.get('job_title', ''),
            company=data.get('company', ''),
            responsibilities=data.get('responsibilities', ''),
        )
        return JsonResponse({'bullets': bullets, 'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e), 'success': False}, status=500)


@login_required(login_url='login')
@csrf_exempt
@require_POST
def ai_suggest_skills(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    try:
        data = json.loads(request.body)
        current_skills = ', '.join([s.name for s in resume.skills.all()])
        suggestions = generate_skills_suggestions(
            job_title=data.get('job_title', ''),
            current_skills=current_skills,
        )
        return JsonResponse({'suggestions': suggestions, 'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e), 'success': False}, status=500)


@login_required(login_url='login')
@csrf_exempt
@require_POST
def ai_optimize(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    try:
        resume_data = {
            'name': resume.full_name,
            'summary': resume.professional_summary,
            'experience': [
                {'title': exp.job_title, 'company': exp.company, 'description': exp.description}
                for exp in resume.experiences.all()
            ],
            'skills': [s.name for s in resume.skills.all()],
        }
        optimized = optimize_resume_content(resume_data)
        return JsonResponse({'optimized': optimized, 'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e), 'success': False}, status=500)
