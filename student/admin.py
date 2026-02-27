from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Student, StudentCourse


class StudentCourseInline(admin.TabularInline):
    model = StudentCourse
    extra = 0
    readonly_fields = ('purchased_at',)
    fields = ('course', 'status', 'purchased_at', 'approved_at')


@admin.register(Student)
class StudentAdmin(UserAdmin):
    inlines = [StudentCourseInline]
    list_display = ('username', 'std_reg_no', 'first_name', 'last_name', 'email', 'std_dept', 'std_year_of_admission', 'role', 'is_active')
    list_filter = ('role', 'std_dept', 'is_active', 'is_staff')
    search_fields = ('username', 'std_reg_no', 'first_name', 'last_name', 'email')
    ordering = ('std_reg_no',)
    fieldsets = UserAdmin.fieldsets + (
        ('Student Info', {
            'fields': ('role', 'std_reg_no', 'std_dept', 'std_year_of_admission', 'std_age', 'std_phone_no', 'std_pic')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Student Info', {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'email', 'role', 'std_reg_no', 'std_dept', 'std_year_of_admission', 'std_age', 'std_phone_no', 'std_pic')
        }),
    )


@admin.register(StudentCourse)
class StudentCourseAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'status', 'purchased_at', 'approved_at')
    list_filter = ('status',)
    search_fields = ('student__std_reg_no', 'student__first_name', 'course__course_name')
    readonly_fields = ('purchased_at',)
    list_editable = ('status',)
    date_hierarchy = 'purchased_at'
    ordering = ('-purchased_at',)