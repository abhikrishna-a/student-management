from django.shortcuts import redirect
from django.contrib import messages


class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Public paths — check here in __call__, not process_view
        public_paths = ['/', '/login/', '/register/', '/logout/']
        
        if any(request.path == path for path in public_paths):
            return self.get_response(request)

        if request.path.startswith('/admin/'):
            return self.get_response(request)

        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('login')

        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.path.startswith('/admin/'):
            return None

        public_paths = ['/', '/login/', '/register/', '/logout/']
        if request.path in public_paths:
            return None

        if not request.user.is_authenticated:
            return None  # already handled in __call__

        # Role-based access control
        if hasattr(request.user, 'role'):
            user_role = request.user.role

            if user_role == 'STUDENT' and request.path.startswith('/principal/'):
                messages.error(request, 'Access denied. Principal access only.')
                return redirect('student_dashboard')

            if user_role == 'PRINCIPAL' and request.path.startswith('/student/'):
                messages.error(request, 'Access denied. Student access only.')
                return redirect('principal_dashboard')

        return None