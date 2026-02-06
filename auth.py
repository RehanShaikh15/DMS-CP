from functools import wraps
from flask import session, redirect, url_for, flash

def admin_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if "admin_id" not in session:
            flash("Please login to access this page", "warning")
            return redirect(url_for("admin_login"))
        return view_func(*args, **kwargs)
    return wrapped_view
