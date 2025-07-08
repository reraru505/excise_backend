from functools import wraps
from .permissions import HasAppPermission, PermissionAction

def has_app_permission(app_label: str, action: PermissionAction):
    """
    Decorator factory that returns a decorator applying HasAppPermission.
    Usage: @has_app_permission('user', 'create')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            permission = HasAppPermission(app_label, action)
            if not permission.has_permission(request, None):
                # The PermissionDenied will be raised by has_permission
                pass  # This line won't be reached if permission is denied
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator
