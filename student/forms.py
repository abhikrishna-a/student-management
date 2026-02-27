from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import RegexValidator
from .models import Student, StudentCourse
from principal.models import Department
import datetime


class StudentRegistrationForm(UserCreationForm):

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'input-field w-full px-4 py-3 rounded-lg text-slate-700 placeholder-slate-400',
            'placeholder': 'student@example.com'
        })
    )
    first_name = forms.CharField(
        max_length=30, required=True,
        widget=forms.TextInput(attrs={
            'class': 'input-field w-full px-4 py-3 rounded-lg text-slate-700',
            'placeholder': 'John'
        })
    )
    last_name = forms.CharField(
        max_length=150, required=True,
        widget=forms.TextInput(attrs={
            'class': 'input-field w-full px-4 py-3 rounded-lg text-slate-700',
            'placeholder': 'Doe'
        })
    )
    std_reg_no = forms.CharField(
        max_length=12, required=True,
        widget=forms.TextInput(attrs={
            'class': 'input-field w-full px-4 py-3 rounded-lg text-slate-700',
            'placeholder': 'REG2024001'
        })
    )
    std_dept = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        empty_label="Select Department",
        widget=forms.Select(attrs={
            'class': 'input-field w-full px-4 py-3 rounded-lg text-slate-700'
        })
    )
    std_year_of_admission = forms.IntegerField(
        required=False, min_value=2000, max_value=2100,
        initial=datetime.datetime.now().year,
        widget=forms.NumberInput(attrs={
            'class': 'input-field w-full px-4 py-3 rounded-lg text-slate-700',
            'placeholder': '2024'
        })
    )
    std_age = forms.IntegerField(
        required=False, min_value=10, max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'input-field w-full px-4 py-3 rounded-lg text-slate-700',
            'placeholder': '20'
        })
    )
    std_phone_no = forms.CharField(
        max_length=10, required=False,
        validators=[RegexValidator(regex=r'^\d{10}$', message="Enter a valid 10-digit phone number.")],
        widget=forms.TextInput(attrs={
            'class': 'input-field w-full px-4 py-3 rounded-lg text-slate-700',
            'placeholder': '9876543210'
        })
    )
    std_pic = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'input-field w-full px-4 py-3 rounded-lg text-slate-700',
            'accept': 'image/*'
        })
    )

    class Meta:
        model = Student
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'input-field w-full px-4 py-3 rounded-lg text-slate-700',
            'placeholder': 'john_doe'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'input-field w-full px-4 py-3 rounded-lg text-slate-700',
            'placeholder': '••••••••'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'input-field w-full px-4 py-3 rounded-lg text-slate-700',
            'placeholder': '••••••••'
        })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Student.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean_std_reg_no(self):
        std_reg_no = self.cleaned_data.get('std_reg_no')
        if Student.objects.filter(std_reg_no=std_reg_no).exists():
            raise forms.ValidationError("This registration number is already in use.")
        return std_reg_no

    def save(self, commit=True):
        student = super().save(commit=False)
        student.email = self.cleaned_data['email']
        student.first_name = self.cleaned_data['first_name']
        student.last_name = self.cleaned_data['last_name']
        student.std_reg_no = self.cleaned_data['std_reg_no']
        student.std_dept = self.cleaned_data.get('std_dept')
        student.std_year_of_admission = self.cleaned_data.get('std_year_of_admission') or datetime.datetime.now().year
        student.std_age = self.cleaned_data.get('std_age')
        student.std_phone_no = self.cleaned_data.get('std_phone_no', '')
        student.role = 'STUDENT'
        if self.cleaned_data.get('std_pic'):
            student.std_pic = self.cleaned_data['std_pic']
        if commit:
            student.save()
        return student


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'input-field w-full px-4 py-3 rounded-lg text-slate-700 placeholder-slate-400',
            'placeholder': 'username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input-field w-full px-4 py-3 rounded-lg text-slate-700 placeholder-slate-400',
            'placeholder': '••••••••'
        })
    )


class StudentProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'first_name', 'last_name', 'email',
            'std_reg_no', 'std_dept', 'std_year_of_admission',
            'std_age', 'std_phone_no', 'std_pic'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'input-field w-full px-4 py-3 rounded-lg text-slate-700'}),
            'last_name': forms.TextInput(attrs={'class': 'input-field w-full px-4 py-3 rounded-lg text-slate-700'}),
            'email': forms.EmailInput(attrs={'class': 'input-field w-full px-4 py-3 rounded-lg text-slate-700'}),
            'std_reg_no': forms.TextInput(attrs={'class': 'input-field w-full px-4 py-3 rounded-lg text-slate-700', 'readonly': True}),
            'std_dept': forms.Select(attrs={'class': 'input-field w-full px-4 py-3 rounded-lg text-slate-700'}),
            'std_year_of_admission': forms.NumberInput(attrs={'class': 'input-field w-full px-4 py-3 rounded-lg text-slate-700'}),
            'std_age': forms.NumberInput(attrs={'class': 'input-field w-full px-4 py-3 rounded-lg text-slate-700'}),
            'std_phone_no': forms.TextInput(attrs={'class': 'input-field w-full px-4 py-3 rounded-lg text-slate-700'}),
            'std_pic': forms.FileInput(attrs={'class': 'input-field w-full px-4 py-3 rounded-lg text-slate-700', 'accept': 'image/*'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Student.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email


class StudentCourseForm(forms.ModelForm):
    class Meta:
        model = StudentCourse
        fields = ['student', 'course', 'status']
        widgets = {
            'student': forms.Select(attrs={'class': 'input-field w-full px-4 py-3 rounded-lg text-slate-700'}),
            'course': forms.Select(attrs={'class': 'input-field w-full px-4 py-3 rounded-lg text-slate-700'}),
            'status': forms.Select(attrs={'class': 'input-field w-full px-4 py-3 rounded-lg text-slate-700'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get('student')
        course = cleaned_data.get('course')
        if student and course:
            qs = StudentCourse.objects.filter(student=student, course=course)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(f"{student} is already enrolled in {course}.")
        return cleaned_data