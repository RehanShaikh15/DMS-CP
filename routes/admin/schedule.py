from flask import render_template, redirect, url_for, flash, request, jsonify
from . import admin_bp
from models import db, Faculty, Department, Subject, AcademicClass, Classroom, Timetable, AcademicCalendar, FacultyLeave
from forms import DailyScheduleForm, TimetableForm, ClassroomFilterForm
from services.scheduler_service import ConflictEngine
from auth import admin_required
from datetime import datetime, date, timedelta, time
from sqlalchemy.exc import IntegrityError

@admin_bp.route("/admin/schedule", methods=["GET", "POST"])
@admin_required
def admin_schedule():
    """Unified Schedule Center"""
    active_tab = request.args.get('tab', 'manage')
    
    manage_form = TimetableForm()
    classroom_form = ClassroomFilterForm()
    daily_form = DailyScheduleForm()

    # Populate choices
    manage_form.department_id.choices = [(d.id, d.name) for d in Department.query.order_by(Department.name).all()]
    manage_form.faculty_id.choices = [(f.id, f.name) for f in Faculty.query.order_by(Faculty.name).all()]
    manage_form.subject_id.choices = [(s.id, s.subject_name) for s in Subject.query.order_by(Subject.subject_name).all()]
    manage_form.academic_class_id.choices = [(c.id, c.name) for c in AcademicClass.query.order_by(AcademicClass.name).all()]
    manage_form.classroom_id.choices = [(c.id, c.room_code) for c in Classroom.query.order_by(Classroom.room_code).all()]
    
    classroom_form.classroom_id.choices = [(c.id, c.room_code) for c in Classroom.query.order_by(Classroom.room_code).all()]

    DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    TIMES = ["09:00", "10:00", "11:00", "12:00", "14:00", "15:00"]
    
    # 1. MANAGE TAB (Weekly Grid)
    manage_grid = {d: {t: None for t in TIMES} for d in DAYS}
    all_slots = Timetable.query.all()
    for slot in all_slots:
        t = slot.start_time.strftime("%H:%M")
        if t in TIMES:
            manage_grid[slot.day][t] = slot

    if active_tab == 'manage' and manage_form.validate_on_submit():
        try:
            start_dt = datetime.strptime(manage_form.start_time.data, "%H:%M").time()
            end_dt = (datetime.combine(date.today(), start_dt) + timedelta(hours=1)).time()
            
            # Check Conflicts via Engine
            conflicts = ConflictEngine.check_conflicts(
                day=manage_form.day.data,
                start_time=start_dt,
                end_time=end_dt,
                faculty_id=manage_form.faculty_id.data,
                academic_class_id=manage_form.academic_class_id.data,
                classroom_id=manage_form.classroom_id.data,
                subject_id=manage_form.subject_id.data
            )

            if conflicts:
                for conflict in conflicts:
                    flash(f"Conflict: {conflict}", "danger")
                
                # Auto-suggest next slot
                suggested_day, suggested_time = ConflictEngine.find_next_available_slot(
                    faculty_id=manage_form.faculty_id.data,
                    academic_class_id=manage_form.academic_class_id.data,
                    classroom_id=manage_form.classroom_id.data
                )
                if suggested_day:
                     flash(f"Suggestion: Next available slot for this Faculty/Class/Room combination is {suggested_day} at {suggested_time}", "info")
                else:
                     flash("No available slots found for this combination!", "warning")

                return redirect(url_for('admin.admin_schedule', tab='manage'))

            slot = Timetable(
                day=manage_form.day.data,
                start_time=start_dt,
                end_time=end_dt,
                faculty_id=manage_form.faculty_id.data,
                subject_id=manage_form.subject_id.data,
                academic_class_id=manage_form.academic_class_id.data,
                classroom_id=manage_form.classroom_id.data
            )
            db.session.add(slot)
            db.session.commit()
            flash("Timetable slot added successfully", "success")
            return redirect(url_for('admin.admin_schedule', tab='manage'))

        except IntegrityError:
            db.session.rollback()
            flash("Error: Database Constraint Violation (Duplicate Entry)", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"An unexpected error occurred: {str(e)}", "danger")
    
    # 2. CLASSROOM TAB
    classroom_grid = {d: {t: None for t in TIMES} for d in DAYS}
    selected_classroom = None
    
    if active_tab == 'classroom' and classroom_form.validate_on_submit():
        c_id = classroom_form.classroom_id.data
        selected_classroom = Classroom.query.get(c_id)
        if selected_classroom:
            c_slots = Timetable.query.filter_by(classroom_id=c_id).all()
            for slot in c_slots:
                t = slot.start_time.strftime("%H:%M")
                if t in TIMES:
                    classroom_grid[slot.day][t] = slot
    
    # 3. DAILY TAB
    daily_schedule_data = []
    selected_date = date.today()
    day_name = selected_date.strftime("%A")

    calendar_event = AcademicCalendar.query.filter_by(date=selected_date).first()
    
    # Auto-detect weekend
    if not calendar_event and selected_date.weekday() in [5, 6]:
        calendar_event = AcademicCalendar(
            date=selected_date,
            description="Weekend",
            is_holiday=True,
            type="Holiday"
        )

    if active_tab == 'daily' and daily_form.validate_on_submit():
        selected_date = daily_form.date.data
        day_name = selected_date.strftime("%A")
        
        # Re-fetch calendar event if date changed
        calendar_event = AcademicCalendar.query.filter_by(date=selected_date).first()

        # Auto-detect weekend
        if not calendar_event and selected_date.weekday() in [5, 6]:
            calendar_event = AcademicCalendar(
                date=selected_date,
                description="Weekend",
                is_holiday=True,
                type="Holiday"
            )

    # Always fetch slots for the selected date (even if not POST, to show today's schedule)
    d_slots = Timetable.query.filter_by(day=day_name).order_by(Timetable.start_time).all()
    leaves = FacultyLeave.query.filter(
        FacultyLeave.status == "Approved",
        FacultyLeave.start_date <= selected_date,
        FacultyLeave.end_date >= selected_date
    ).all()
    leave_ids = {l.faculty_id for l in leaves}
    
    for slot in d_slots:
        daily_schedule_data.append({
            "slot": slot,
            "is_blocked": slot.faculty_id in leave_ids
        })

    return render_template(
        "admin/admin_schedule.html",
        active_tab=active_tab,
        manage_form=manage_form,
        classroom_form=classroom_form,
        daily_form=daily_form,
        manage_grid=manage_grid,
        classroom_grid=classroom_grid,
        selected_classroom=selected_classroom,
        daily_schedule_data=daily_schedule_data,
        selected_date=selected_date,
        day_name=day_name,
        days=DAYS,
        times=TIMES,
        calendar_event=calendar_event
    )

@admin_bp.route("/admin/schedule/delete/<int:id>", methods=["POST"])
@admin_required
def delete_schedule(id):
    """Delete a timetable slot"""
    slot = Timetable.query.get_or_404(id)
    try:
        db.session.delete(slot)
        db.session.commit()
        flash("Timetable slot deleted successfully", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting slot: {str(e)}", "danger")
    
    return redirect(url_for('admin.admin_schedule', tab='manage'))


@admin_bp.route("/api/faculty/<int:faculty_id>/subjects")
@admin_required
def get_faculty_subjects(faculty_id):
    """Get subjects assigned to a specific faculty"""
    faculty = Faculty.query.get_or_404(faculty_id)
    return jsonify({
        "subjects": [{"id": fs.subject.id, "name": fs.subject.subject_name} for fs in faculty.subjects]
    })
