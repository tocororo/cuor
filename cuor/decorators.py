from flask import abort
from functools import wraps
from flask_login import current_user
from cuor.organizations.permissions import curator_permission


def curator_permission(fn):
    """Check user permissions."""
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        """Decorated view."""
        if not current_user.is_authenticated:
            abort(401)
        if not curator_permission.can():
            abort(403)
        return fn(*args, **kwargs)
    return decorated_view
