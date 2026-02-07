from flask import Blueprint, redirect, url_for
from auth import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route("/admin/dashboard")
@admin_required
def dashboard():
    """Redirect to main admin view"""
    return redirect(url_for("admin.faculty_list"))

from . import faculty, academics, schedule, hr, analytics, exports
