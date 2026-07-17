document.addEventListener('DOMContentLoaded', function() {
    initNavbarScroll();
    initScrollAnimations();
    initModals();
    initToasts();
    initFormHandling();
    initAIButtons();
    initDeleteButtons();
    initTemplateSelector();
    initTypingEffect();
});

function initNavbarScroll() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;
    window.addEventListener('scroll', () => {
        navbar.classList.toggle('scrolled', window.scrollY > 50);
    });
}

function initScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

    document.querySelectorAll('.animate-on-scroll').forEach(el => observer.observe(el));
}

function initModals() {
    document.querySelectorAll('[data-modal]').forEach(trigger => {
        trigger.addEventListener('click', function(e) {
            e.preventDefault();
            openModal(this.getAttribute('data-modal'));
        });
    });

    document.querySelectorAll('.modal-close, .modal-cancel').forEach(btn => {
        btn.addEventListener('click', function() {
            const modal = this.closest('.modal-overlay');
            if (modal) closeModal(modal.id);
        });
    });

    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', function(e) {
            if (e.target === this) closeModal(this.id);
        });
    });
}

function openModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
}

function initToasts() {
    document.querySelectorAll('.toast-message').forEach(msg => {
        showToast(msg.dataset.message, msg.dataset.type || 'success');
        msg.remove();
    });
}

function showToast(message, type = 'info') {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const icons = {
        success: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg>',
        error: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><path d="M15 9l-6 6M9 9l6 6"/></svg>',
        info: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>'
    };

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `${icons[type] || icons.info}<span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100px)';
        toast.style.transition = 'all 0.4s ease';
        setTimeout(() => toast.remove(), 400);
    }, 4000);
}

function initFormHandling() {
    document.querySelectorAll('form[data-ajax]').forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            try {
                const response = await fetch(this.action, {
                    method: this.method || 'POST',
                    body: formData,
                    headers: { 'X-CSRFToken': getCSRFToken() },
                });
                if (response.ok) {
                    const data = await response.json();
                    if (data.success) {
                        showToast('Saved successfully!', 'success');
                        if (data.redirect) window.location.href = data.redirect;
                        if (data.reload) location.reload();
                    }
                }
            } catch (err) {
                showToast('An error occurred.', 'error');
            }
        });
    });
}

function initAIButtons() {
    document.querySelectorAll('.btn-ai-generate').forEach(btn => {
        btn.addEventListener('click', async function() {
            const action = this.dataset.aiAction;
            const resumeId = this.dataset.resumeId;
            const originalText = this.innerHTML;

            this.innerHTML = '<span class="spinner"></span> Generating...';
            this.disabled = true;

            try {
                let endpoint = '';
                let body = {};

                if (action === 'summary') {
                    endpoint = `/resume/${resumeId}/ai/summary/`;
                    body = {
                        job_title: document.getElementById('ai_job_title')?.value || '',
                        experience: document.getElementById('ai_experience')?.value || '',
                        skills: document.getElementById('ai_skills')?.value || '',
                    };
                } else if (action === 'bullets') {
                    endpoint = `/resume/${resumeId}/ai/bullets/`;
                    body = {
                        job_title: document.getElementById('ai_exp_title')?.value || '',
                        company: document.getElementById('ai_exp_company')?.value || '',
                        responsibilities: document.getElementById('ai_exp_responsibilities')?.value || '',
                    };
                } else if (action === 'skills') {
                    endpoint = `/resume/${resumeId}/ai/skills/`;
                    body = { job_title: document.getElementById('ai_skill_title')?.value || '' };
                } else if (action === 'optimize') {
                    endpoint = `/resume/${resumeId}/ai/optimize/`;
                    body = {};
                }

                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
                    body: JSON.stringify(body),
                });

                const data = await response.json();

                if (data.success) {
                    if (action === 'summary' && data.summary) {
                        const target = document.getElementById('ai_summary_result');
                        if (target) { target.textContent = data.summary; target.style.display = 'block'; }
                        const summaryField = document.getElementById('professional_summary');
                        if (summaryField) summaryField.value = data.summary;
                        showToast('Summary generated!', 'success');
                    } else if (action === 'bullets' && data.bullets) {
                        const target = document.getElementById('ai_bullets_result');
                        if (target) {
                            const bullets = typeof data.bullets === 'object' && data.bullets.bullets ? data.bullets.bullets : Array.isArray(data.bullets) ? data.bullets : [];
                            target.textContent = bullets.join('\n');
                            target.style.display = 'block';
                        }
                        showToast('Bullets generated!', 'success');
                    } else if (action === 'skills' && data.suggestions) {
                        const target = document.getElementById('ai_skills_result');
                        if (target) { target.textContent = JSON.stringify(data.suggestions, null, 2); target.style.display = 'block'; }
                        showToast('Skills suggested!', 'success');
                    } else if (action === 'optimize' && data.optimized) {
                        const target = document.getElementById('ai_optimize_result');
                        if (target) { target.textContent = JSON.stringify(data.optimized, null, 2); target.style.display = 'block'; }
                        showToast('Resume optimized!', 'success');
                    }
                } else {
                    showToast(data.error || 'AI generation failed.', 'error');
                }
            } catch (err) {
                showToast('Error connecting to AI service.', 'error');
            }

            this.innerHTML = originalText;
            this.disabled = false;
        });
    });
}

function initDeleteButtons() {
    document.querySelectorAll('.btn-delete-item').forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.preventDefault();
            if (!confirm('Are you sure you want to delete this item?')) return;

            try {
                const response = await fetch(this.dataset.deleteUrl, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': getCSRFToken(), 'Content-Type': 'application/json' },
                });
                if (response.ok) {
                    const item = this.closest('.item-card, .skill-chip');
                    if (item) {
                        item.style.opacity = '0';
                        item.style.transform = 'translateX(30px) scale(0.95)';
                        item.style.transition = 'all 0.4s ease';
                        setTimeout(() => item.remove(), 400);
                    }
                    showToast('Deleted successfully!', 'success');
                }
            } catch (err) {
                showToast('Error deleting item.', 'error');
            }
        });
    });
}

function initTemplateSelector() {
    document.querySelectorAll('.template-option').forEach(option => {
        option.addEventListener('click', function() {
            document.querySelectorAll('.template-option').forEach(o => o.classList.remove('active'));
            this.classList.add('active');
            const input = document.getElementById('selected_template');
            if (input) input.value = this.dataset.template;
        });
    });
}

function initTypingEffect() {
    const el = document.querySelector('.typing-text');
    if (!el) return;
    const texts = JSON.parse(el.dataset.texts || '[]');
    if (!texts.length) return;
    let textIndex = 0, charIndex = 0, isDeleting = false;

    function type() {
        const current = texts[textIndex];
        el.textContent = isDeleting ? current.substring(0, charIndex--) : current.substring(0, charIndex++);

        let delay = isDeleting ? 40 : 80;
        if (!isDeleting && charIndex === current.length + 1) { delay = 2000; isDeleting = true; }
        else if (isDeleting && charIndex < 0) { isDeleting = false; textIndex = (textIndex + 1) % texts.length; delay = 500; }

        setTimeout(type, delay);
    }
    type();
}

function getCSRFToken() {
    const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
    return cookie ? cookie.split('=')[1] : '';
}
