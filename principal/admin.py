from django.contrib import admin
from .models import Department, AddOnCourse


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('dept_name', 'dept_description', 'course_count')
    search_fields = ('dept_name',)
    ordering = ('dept_name',)

    def course_count(self, obj):
        return AddOnCourse.objects.filter(department=obj).count()
    course_count.short_description = 'Courses'


class AddOnCourseInline(admin.TabularInline):
    model = AddOnCourse
    extra = 0
    fields = ('course_id', 'course_name', 'course_price')
    readonly_fields = ('created_at',)


@admin.register(AddOnCourse)
class AddOnCourseAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'course_name', 'department', 'formatted_price', 'created_at')
    list_filter = ('department',)
    search_fields = ('course_id', 'course_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'formatted_price')
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Course Identity', {
            'fields': ('course_id', 'course_name', 'department')
        }),
        ('Details', {
            'fields': ('course_description', 'course_price', 'formatted_price')
        }),
        ('Meta', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )