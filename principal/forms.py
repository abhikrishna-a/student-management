from django import forms
from .models import Department, AddOnCourse


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['dept_name', 'dept_description']
        widgets = {
            'dept_name': forms.TextInput(attrs={
                'class': 'input-field w-full px-4 py-3 rounded-lg text-slate-700',
                'placeholder': 'Computer Science'
            }),
            'dept_description': forms.Textarea(attrs={
                'class': 'input-field w-full px-4 py-3 rounded-lg text-slate-700',
                'rows': 3,
                'placeholder': 'Brief description of the department...'
            }),
        }

    def clean_dept_name(self):
        name = self.cleaned_data.get('dept_name')
        qs = Department.objects.filter(dept_name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("A department with this name already exists.")
        return name


class AddOnCourseForm(forms.ModelForm):
    class Meta:
        model = AddOnCourse
        fields = ['course_id', 'course_name', 'department', 'course_description', 'course_price']
        widgets = {
            'course_id': forms.TextInput(attrs={
                'class': 'input-field w-full px-4 py-3 rounded-lg text-slate-700',
                'placeholder': 'CRS-001'
            }),
            'course_name': forms.TextInput(attrs={
                'class': 'input-field w-full px-4 py-3 rounded-lg text-slate-700',
                'placeholder': 'Advanced Python Programming'
            }),
            'department': forms.Select(attrs={
                'class': 'input-field w-full px-4 py-3 rounded-lg text-slate-700'
            }),
            'course_description': forms.Textarea(attrs={
                'class': 'input-field w-full px-4 py-3 rounded-lg text-slate-700',
                'rows': 4,
                'placeholder': 'Describe what students will learn...'
            }),
            'course_price': forms.NumberInput(attrs={
                'class': 'input-field w-full px-4 py-3 rounded-lg text-slate-700',
                'min': 0,
                'placeholder': '999'
            }),
        }

    def clean_course_id(self):
        course_id = self.cleaned_data.get('course_id')
        if not course_id:
            return course_id
        qs = AddOnCourse.objects.filter(course_id=course_id)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("This course ID is already in use.")
        return course_id

    def clean_course_price(self):
        price = self.cleaned_data.get('course_price')
        if price is not None and price < 0:
            raise forms.ValidationError("Price cannot be negative.")
        return price