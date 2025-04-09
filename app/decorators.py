from functools import wraps
from flask import abort
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401) # Unauthorized
        if current_user.role != 'Administrator':
            abort(403) # Forbidden
        return f(*args, **kwargs)
    return decorated_function

# Optional: Decorator für Techniker+Admin (falls benötigt)
def technician_or_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if current_user.role not in ['Administrator', 'Techniker']:
             abort(403)
        return f(*args, **kwargs)
    return decorated_function