from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Faculty, Timetable, FacultyAttendance, FacultyLeave
from faculty_auth import faculty_required
from forms import FacultyLeaveForm
from datetime import datetime, date
from collections import defaultdict

faculty_bp = Blueprint('faculty', __name__)

@faculty_bp.route("/faculty/dashboard")
@faculty_required
def dashboard():
    faculty_id = session["faculty_id"]
    faculty = Faculty.query.get_or_404(faculty_id)

    # Attendance Stats
    total_days = len(faculty.attendance_records)
    present_days = len([a for a in faculty.attendance_records if a.status == 'Present'])
    attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0

    # Timetable
    slots = (
        Timetable.query
        .filter_by(faculty_id=faculty_id)
        .order_by(Timetable.day, Timetable.start_time)
        .all()
    )

    week = defaultdict(list)
    week_data = defaultdict(list)
    for slot in slots:
        week_data[slot.day].append(slot)

    # Sort days
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    week = {day: week_data[day] for day in days_order if day in week_data}

    return render_template(
        "faculty/faculty_dashboard.html",
        week=week,
        attendance_percentage=round(attendance_percentage, 2),
        present_days=present_days,
        total_days=total_days
    )

@faculty_bp.route("/faculty/attendance")
@faculty_required
def attendance_view():
    records = FacultyAttendance.query.filter_by(
        faculty_id=session["faculty_id"]
    ).order_by(FacultyAttendance.date.desc()).all()

    return render_template(
        "faculty/attendance_view.html",
        records=records
    )

@faculty_bp.route("/faculty/leave/apply", methods=["GET", "POST"])
@faculty_required
def apply_leave():
    form = FacultyLeaveForm()
    faculty_id = session["faculty_id"]

    if form.validate_on_submit():
        try:
            leave = FacultyLeave(
                faculty_id=faculty_id,
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                reason=form.reason.data
            )
            db.session.add(leave)
            db.session.commit()

            flash("Leave request submitted", "success")
            return redirect(url_for("faculty.my_leaves"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error submitting leave request: {str(e)}", "danger")

    return render_template("faculty/apply_leave.html", form=form)


@faculty_bp.route("/faculty/leaves")
@faculty_required
def my_leaves():
    faculty_id = session["faculty_id"]

    leaves = FacultyLeave.query.filter_by(
        faculty_id=faculty_id
    ).order_by(FacultyLeave.applied_at.desc()).all()

    return render_template(
        "faculty/my_leaves.html",
        leaves=leaves
    )
