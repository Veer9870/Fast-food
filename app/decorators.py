from functools import wraps
from flask import abort
from flask_login import current_user

def role_required(*roles):
    """
    Decorator to restrict access to users with specific roles.
    Usage: @role_required('admin', 'manager')
    """
    def wrapper(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            if not current_user.has_role(*roles):
                abort(403) # Forbidden
            return func(*args, **kwargs)
        return decorated_view
    return wrapper

def admin_required(func):
    return role_required('super_admin', 'admin')(func)
