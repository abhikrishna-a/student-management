from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Student, StudentCourse
from .forms import StudentRegistrationForm, LoginForm, StudentProfileUpdateForm
from principal.models import AddOnCourse
from django.core.mail import send_mail
from django.conf import settings

def landing_view(request):
    return render(request, 'student/landing.html')

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            name = user.first_name or user.username
            messages.success(request, f'Welcome back, {name}!')
            if user.role == 'PRINCIPAL':
                return redirect('principal_dashboard')
            else:
                return redirect('student_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'student/login.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save()

            send_mail(
                subject='Welcome to Our Platform',
                message=f'Hi {student.username},\n\nYour account has been created successfully!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[student.email],
                fail_silently=False,
            )

            login(request, student)
            messages.success(request, 'Account created successfully! Welcome!')
            return redirect('student_dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}' if field != '__all__' else error)
    else:
        form = StudentRegistrationForm()

    return render(request, 'student/registration.html', {'form': form})


@login_required
def purchase_course(request):
    student = request.user

    if request.method == 'POST':
        course_ids = request.POST.get('course_ids', '')
        if course_ids:
            ids = [i.strip() for i in course_ids.split(',') if i.strip()]
            for course_id in ids:
                try:
                    course = AddOnCourse.objects.get(pk=course_id)
                    StudentCourse.objects.get_or_create(student=student, course=course)
                except (AddOnCourse.DoesNotExist, ValueError):
                    pass
            messages.success(request, 'Course purchase request submitted successfully!')
        else:
            messages.error(request, 'No courses selected.')
        return redirect('purchase_course')

    
    if student.std_dept:
        all_courses = AddOnCourse.objects.select_related('department').filter(department=student.std_dept)
    else:
        all_courses = AddOnCourse.objects.select_related('department').all()

    purchased = StudentCourse.objects.filter(student=student).select_related('course')
    purchased_map = {p.course.pk: p.status for p in purchased}

    courses_with_status = []
    for course in all_courses:
        courses_with_status.append({
            'course': course,
            'status': purchased_map.get(course.pk),
        })

    context = {
        'courses_with_status': courses_with_status,
        'total_courses': all_courses.count(),
        'student_dept': student.std_dept,
    }
    return render(request, 'student/purchasecourse.html', context)

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        try:
            user = User.objects.get(email=email)
            # Generate token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Build reset URL
            reset_url = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )
            
            # Send email
            send_mail(
                subject='Password Reset - StudentManage',
                message=f'Click the link below to reset your password:\n\n{reset_url}\n\nThis link expires in 24 hours.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            messages.success(request, 'Reset link sent! Please check your inbox.')
            return redirect('forgot_password')
        
        except User.DoesNotExist:
            # Don't reveal whether email exists (security best practice)
            messages.success(request, 'If that email is registered, a reset link has been sent.')
            return redirect('forgot_password')
    
    return render(request, 'forgot_password.html')


@login_required
def profile(request):
    student = request.user

    if request.method == 'POST':
        update_type = request.POST.get('update_type')

       
        if update_type == 'profile_pic':
            if request.FILES.get('std_pic'):
                student.std_pic = request.FILES['std_pic']
                student.save()
                messages.success(request, 'Profile picture updated successfully!')
            else:
                messages.error(request, 'Please select an image to upload.')
            return redirect('profile')

        
        else:
            form = StudentProfileUpdateForm(request.POST, request.FILES, instance=student)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('profile')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}' if field != '__all__' else error)
                return render(request, 'student/profile.html', {'form': form, 'student': student})

    else:
        form = StudentProfileUpdateForm(instance=student)

    return render(request, 'student/profile.html', {'form': form, 'student': student})



@login_required
def student_dashboard(request):
    student = request.user
    enrolled_courses = StudentCourse.objects.filter(student=student).select_related('course__department')
    approved = enrolled_courses.filter(status='APPROVED')
    pending = enrolled_courses.filter(status='PENDING')
    rejected = enrolled_courses.filter(status='REJECTED')
    
    total_spent = sum(item.course.course_price for item in approved)

    context = {
        'student': student,
        'enrolled_courses': enrolled_courses,
        'approved_courses': approved,
        'pending_courses': pending,
        'rejected_courses': rejected,
        'total_spent': total_spent,
    }
    return render(request, 'student/student_dashboard.html', context)
def course(request):
    return render(request, 'student/course.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out!')
    return redirect('login')