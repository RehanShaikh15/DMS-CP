from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from models import db, Admin, Faculty
from forms import AdminLoginForm, FacultyLoginForm, FacultySetPasswordForm

auth_bp = Blueprint('auth', __name__)

# --- ADMIN AUTH ---

@auth_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    form = AdminLoginForm()

    if form.validate_on_submit():
        try:
            admin = Admin.query.filter_by(username=form.username.data).first()

            if admin and admin.check_password(form.password.data):
                session.permanent = True
                session["admin_id"] = admin.id
                session["admin_username"] = admin.username
                flash("Login successful", "success")
                return redirect(url_for("admin.faculty_list"))  # Point to Admin BP

            flash("Invalid username or password", "danger")
        except Exception as e:
            flash(f"An error occurred during login: {str(e)}", "danger")

    return render_template("admin/admin_login.html", form=form)


@auth_bp.route("/admin/logout")
def admin_logout():
    session.clear()
    flash("Logged out successfully", "info")
    return redirect(url_for("auth.admin_login"))


# --- FACULTY AUTH ---

@auth_bp.route("/faculty/login", methods=["GET", "POST"])
def faculty_login():
    form = FacultyLoginForm()

    if form.validate_on_submit():
        try:
            faculty = Faculty.query.filter_by(email=form.email.data).first()

            if not faculty:
                flash("Invalid credentials", "danger")
                return redirect(url_for("auth.faculty_login"))

            # 🔹 FIRST TIME LOGIN
            if faculty.password_hash is None:
                session["reset_faculty_id"] = faculty.id
                return redirect(url_for("auth.faculty_set_password"))

            if faculty.check_password(form.password.data):
                session.permanent = True
                session["faculty_id"] = faculty.id
                session["faculty_name"] = faculty.name
                flash("Welcome!", "success")
                return redirect(url_for("faculty.dashboard"))  # Point to Faculty BP

            flash("Invalid credentials", "danger")
        except Exception as e:
            flash(f"An error occurred during login: {str(e)}", "danger")

    return render_template("faculty/faculty_login.html", form=form)


@auth_bp.route("/faculty/set-password", methods=["GET", "POST"])
def faculty_set_password():
    faculty_id = session.get("reset_faculty_id")

    if not faculty_id:
        return redirect(url_for("auth.faculty_login"))

    try:
        faculty = Faculty.query.get_or_404(faculty_id)
    except Exception as e:
        flash(f"Error retrieving faculty: {str(e)}", "danger")
        return redirect(url_for("auth.faculty_login"))

    form = FacultySetPasswordForm()

    if form.validate_on_submit():
        try:
            faculty.set_password(form.password.data)
            db.session.commit()

            session.pop("reset_faculty_id")
            flash("Password set successfully. Please login.", "success")
            return redirect(url_for("auth.faculty_login"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error setting password: {str(e)}", "danger")

    return render_template("faculty/faculty_set_password.html", form=form)


@auth_bp.route("/faculty/logout")
def faculty_logout():
    session.pop("faculty_id", None)
    session.pop("faculty_name", None)
    flash("Logged out", "info")
    return redirect(url_for("auth.faculty_login"))


# --- INDEX REDIRECT ---

@auth_bp.route('/')
def index():
    if "admin_id" in session:
        return redirect(url_for('admin.faculty_list'))
    elif "faculty_id" in session:
        return redirect(url_for('faculty.dashboard'))
    return redirect(url_for('auth.admin_login'))
