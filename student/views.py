from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Student, StudentCourse
from .forms import StudentRegistrationForm, LoginForm, StudentProfileUpdateForm
from principal.models import AddOnCourse


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

    # Filter courses by student's department
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


@login_required
def profile(request):
    student = request.user

    if request.method == 'POST':
        update_type = request.POST.get('update_type')

        # Profile picture only update
        if update_type == 'profile_pic':
            if request.FILES.get('std_pic'):
                student.std_pic = request.FILES['std_pic']
                student.save()
                messages.success(request, 'Profile picture updated successfully!')
            else:
                messages.error(request, 'Please select an image to upload.')
            return redirect('profile')

        # Full profile update
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