from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from student.models import Student, StudentCourse
from principal.models import AddOnCourse, Department


@login_required
def principal_dashboard(request):
    pending_requests = StudentCourse.objects.filter(
        status='PENDING'
    ).select_related('student__std_dept', 'course__department')

    pending_count  = pending_requests.count()
    total_approved = StudentCourse.objects.filter(status='APPROVED').count()
    total_rejected = StudentCourse.objects.filter(status='REJECTED').count()
    total_requests = StudentCourse.objects.count()

    context = {
        'total_students':    Student.objects.filter(role='STUDENT').count(),
        'total_courses':     AddOnCourse.objects.count(),
        'total_departments': Department.objects.count(),
        'pending_requests':  pending_requests,
        'pending_count':     pending_count,
        'total_approved':    total_approved,
        'total_rejected':    total_rejected,
        'total_requests':    total_requests,
        'recent_students':   Student.objects.select_related('std_dept').filter(role='STUDENT').order_by('-date_joined')[:5],
        'recent_courses':    AddOnCourse.objects.select_related('department').order_by('-id')[:5],
    }
    return render(request, 'principal/principal_dashboard.html', context)


@login_required
def view_students(request):
    search_query = request.GET.get('q', '')
    dept_filter  = request.GET.get('dept', '')
    departments  = Department.objects.all()

    students = Student.objects.select_related('std_dept').filter(role='STUDENT')

    if search_query:
        students = students.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)  |
            Q(email__icontains=search_query)       |
            Q(std_reg_no__icontains=search_query)
        )

    if dept_filter:
        students = students.filter(std_dept__pk=dept_filter)

    students = students.annotate(
        total_courses=Count('course_purchases'),
        approved_count=Count(
            'course_purchases',
            filter=Q(course_purchases__status='APPROVED')
        ),
    )

    total                   = students.count()
    total_approved_students = Student.objects.filter(
        role='STUDENT',
        course_purchases__status='APPROVED'
    ).distinct().count()

    return render(request, 'principal/principal_students_list.html', {
        'students':                students,
        'departments':             departments,
        'search_query':            search_query,
        'dept_filter':             dept_filter,
        'total':                   total,
        'total_approved_students': total_approved_students,
    })

@login_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        action      = request.POST.get('action')
        purchase_id = request.POST.get('purchase_id')
        if purchase_id:
            purchase = get_object_or_404(StudentCourse, pk=purchase_id)
            if action == 'approve_purchase':
                purchase.status = 'APPROVED'
                purchase.save()
                messages.success(request, f'Course "{purchase.course.course_name}" approved.')
            elif action == 'reject_purchase':
                purchase.status = 'REJECTED'
                purchase.save()
                messages.error(request, f'Course "{purchase.course.course_name}" rejected.')
        return redirect('student_detail', pk=pk)

    student_courses  = StudentCourse.objects.filter(student=student).select_related('course__department')
    approved_courses = student_courses.filter(status='APPROVED')
    pending_courses  = student_courses.filter(status='PENDING')
    rejected_courses = student_courses.filter(status='REJECTED')
    total_spent      = sum(p.course.course_price for p in approved_courses)

    return render(request, 'principal/principal_student_view.html', {
        'student':          student,
        'student_courses':  student_courses,
        'approved_courses': approved_courses,
        'pending_courses':  pending_courses,
        'rejected_courses': rejected_courses,
        'approved_count':   approved_courses.count(),
        'pending_count':    pending_courses.count(),
        'rejected_count':   rejected_courses.count(),
        'total_spent':      total_spent,
    })


@login_required
def view_courses(request):
    departments  = Department.objects.all()
    dept_filter  = request.GET.get('dept', '')
    search_query = request.GET.get('q', '')

    # FIX: related_name is 'student_purchases', not 'studentcourse'
    # FIX: removed is_active filter — field doesn't exist on AddOnCourse
    courses = AddOnCourse.objects.select_related('department').annotate(
        enrolled_count=Count('student_purchases'),
    )

    if dept_filter:
        courses = courses.filter(department__pk=dept_filter)

    if search_query:
        courses = courses.filter(
            Q(course_name__icontains=search_query) |
            Q(course_id__icontains=search_query)   |
            Q(course_description__icontains=search_query)
        )

    total = courses.count()

    return render(request, 'principal/principal_course_list.html', {
        'courses':                courses,
        'departments':            departments,
        'dept_filter':            dept_filter,
        'search_query':           search_query,
        'total':                  total,
        'total_active_courses':   total,
        'total_inactive_courses': 0,
    })


@login_required
def add_course(request):
    if request.method == 'POST':
        course_name = request.POST.get('course_name', '').strip()
        course_id   = request.POST.get('course_id', '').strip()
        department  = request.POST.get('department')
        description = request.POST.get('course_description', '').strip()
        price       = request.POST.get('course_price', 0)

        if not course_name or not course_id or not department:
            messages.error(request, 'Course name, ID, and department are required.')
            return redirect('add_course')

        try:
            dept = Department.objects.get(pk=department)
            AddOnCourse.objects.create(
                course_name=course_name,
                course_id=course_id,
                department=dept,
                course_description=description,
                course_price=price,
            )
            messages.success(request, f'Course "{course_name}" added successfully.')
            return redirect('view_courses')
        except Department.DoesNotExist:
            messages.error(request, 'Invalid department selected.')
        except Exception as e:
            messages.error(request, f'Error adding course: {e}')

    departments = Department.objects.all()
    return render(request, 'principal/addcourse.html', {
        'departments': departments
    })


@login_required
def delete_course(request, pk):
    course = get_object_or_404(AddOnCourse, pk=pk)
    if request.method == 'POST':
        name = course.course_name
        course.delete()
        messages.success(request, f'Course "{name}" deleted successfully.')
    return redirect('view_courses')


@login_required
def approve_course(request, pk):
    req = get_object_or_404(StudentCourse, pk=pk)
    req.status = 'APPROVED'
    req.save()
    messages.success(request, f'Course "{req.course.course_name}" approved for {req.student.get_full_name()}.')
    return redirect('principal_dashboard')


@login_required
def reject_course(request, pk):
    req = get_object_or_404(StudentCourse, pk=pk)
    req.status = 'REJECTED'
    req.save()
    messages.error(request, f'Course "{req.course.course_name}" rejected for {req.student.get_full_name()}.')
    return redirect('principal_dashboard')