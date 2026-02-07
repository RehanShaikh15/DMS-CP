from flask import render_template, redirect, url_for, flash, request
from . import admin_bp
from models import db, Faculty, Department, FacultyAttendance, FacultyLeave, AcademicCalendar
from forms import AdminAttendanceFilterForm, AcademicCalendarForm
from auth import admin_required
from datetime import date, datetime
import calendar
from sqlalchemy.exc import IntegrityError

@admin_bp.route("/admin/hr", methods=["GET", "POST"])
@admin_required
def admin_hr():
    active_tab = request.args.get('tab', 'attendance')
    
    attendance_form = AdminAttendanceFilterForm()
    attendance_form.department_id.choices = [(d.id, d.name) for d in Department.query.order_by(Department.name).all()]
    
    faculty_list = []
    existing_attendance = {}

    if active_tab == 'attendance' and attendance_form.validate_on_submit():
        dept_id = attendance_form.department_id.data
        selected_date = attendance_form.date.data
        
        faculty_list = Faculty.query.filter_by(department_id=dept_id).all()
        records = FacultyAttendance.query.filter(
            FacultyAttendance.date == selected_date,
            FacultyAttendance.faculty_id.in_([f.id for f in faculty_list])
        ).all()
        existing_attendance = {r.faculty_id: r for r in records}

    leaves = FacultyLeave.query.order_by(FacultyLeave.applied_at.desc()).all()

    return render_template(
        "admin/admin_hr.html",
        active_tab=active_tab,
        attendance_form=attendance_form,
        faculty_list=faculty_list,
        existing_attendance=existing_attendance,
        leaves=leaves
    )

@admin_bp.route("/admin/attendance/save", methods=["POST"])
@admin_required
def save_attendance():
    date_str = request.form.get("date")

    try:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            flash("Invalid date format", "danger")
            return redirect(url_for("admin.admin_hr", tab="attendance"))

        # 1. Check if Weekend (Saturday=5, Sunday=6)
        if selected_date.weekday() in [5, 6]:
            flash("Cannot mark attendance on Weekends (Saturday/Sunday).", "warning")
            return redirect(url_for("admin.admin_hr", tab="attendance"))
        
        # 2. Check Academic Calendar (Holiday)
        calendar_event = AcademicCalendar.query.filter_by(date=selected_date).first()
        if calendar_event and calendar_event.is_holiday:
            flash(f"Cannot mark attendance: {calendar_event.description} (Holiday)", "warning")
            return redirect(url_for("admin.admin_hr", tab="attendance"))

        for key, value in request.form.items():
            if not key.startswith("status_"):
                continue

            faculty_id = int(key.split("_")[1])

            # Check if faculty is on approved leave
            existing_leave = FacultyLeave.query.filter(
                FacultyLeave.faculty_id == faculty_id,
                FacultyLeave.status == "Approved",
                FacultyLeave.start_date <= selected_date,
                FacultyLeave.end_date >= selected_date
            ).first()

            if existing_leave:
                if value == "Present":
                     flash(f"Warning: Faculty {faculty_id} is on approved leave. Marked as 'Leave'.", "warning")
                     value = "Leave"

            if record := FacultyAttendance.query.filter_by(
                    faculty_id=faculty_id, date=selected_date
            ).first():
                record.status = value
            else:
                db.session.add(FacultyAttendance(
                    faculty_id=faculty_id,
                    date=selected_date,
                    status=value
                ))

        db.session.commit()
        flash("Attendance saved successfully", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error saving attendance: {str(e)}", "danger")

    return redirect(url_for("admin.admin_hr", tab="attendance"))

@admin_bp.route("/admin/leave/<int:leave_id>/approve")
@admin_required
def approve_leave(leave_id):
    try:
        leave = FacultyLeave.query.get_or_404(leave_id)
        if leave.status != "Pending":
            flash("Leave already processed", "warning")
        else:
            leave.status = "Approved"
            db.session.commit()
            flash(f"Leave for {leave.faculty.name} approved.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error approving leave: {str(e)}", "danger")

    return redirect(url_for("admin.admin_hr", tab="leaves"))

@admin_bp.route("/admin/leave/<int:leave_id>/reject")
@admin_required
def reject_leave(leave_id):
    try:
        leave = FacultyLeave.query.get_or_404(leave_id)
        if leave.status != "Pending":
             flash("Leave already processed", "warning")
        else:
            leave.status = "Rejected"
            db.session.commit()
            flash("Leave rejected", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error rejecting leave: {str(e)}", "danger")
    return redirect(url_for('admin.admin_hr', tab='leaves'))


@admin_bp.route("/admin/calendar", methods=["GET", "POST"])
@admin_required
def admin_calendar():
    """Manage Academic Calendar"""
    form = AcademicCalendarForm()
    
    if form.validate_on_submit():
        try:
            event = AcademicCalendar(
                date=form.date.data,
                description=form.description.data,
                type=form.type.data,
                is_holiday=(form.type.data == 'Holiday'),
                is_exam=(form.type.data == 'Exam')
            )
            db.session.add(event)
            db.session.commit()
            flash("Event added successfully", "success")
            return redirect(url_for('admin.admin_calendar'))
        except IntegrityError:
            db.session.rollback()
            flash("An event for this date already exists.", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding event: {str(e)}", "danger")

    events = AcademicCalendar.query.order_by(AcademicCalendar.date).all()
    
    return render_template("admin/admin_calendar.html", form=form, events=events)

@admin_bp.route("/admin/calendar/delete/<int:id>", methods=["POST"])
@admin_required
def delete_calendar_event(id):
    event = AcademicCalendar.query.get_or_404(id)
    try:
        db.session.delete(event)
        db.session.commit()
        flash("Event deleted", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting event: {str(e)}", "danger")
    
    return redirect(url_for('admin.admin_calendar'))
