from functools import wraps
from flask import session, redirect, url_for

def faculty_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "faculty_id" not in session:
            return redirect(url_for("faculty_login"))
        return view(*args, **kwargs)
    return wrapped
