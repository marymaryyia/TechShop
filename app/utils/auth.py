# DECORATORS
# =============================================================================

from functools import wraps

from flask import abort
from flask_login import current_user

def admin_required(f):
    """Require admin role for route access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # ვამოწმებთ არის თუ არა მომხმარებელი შესული და აქვს თუ არა შესაბამისი როლი
        if not current_user.is_authenticated or current_user.role not in ['admin', 'super_admin']:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

