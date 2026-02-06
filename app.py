from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_bootstrap import Bootstrap5
from sqlalchemy import or_
from models import db, Faculty, Department,AcademicClass, Subject, FacultySubject, Admin, Timetable, FacultyAttendance, FacultyLeave, Classroom
from forms import FacultyForm, populate_form_choices, AdminLoginForm, FacultyLoginForm, FacultySetPasswordForm, DepartmentForm, SubjectForm, AcademicClassForm, TimetableForm, AdminAttendanceFilterForm, FacultyLeaveForm, ClassroomForm, ClassroomFilterForm, DailyScheduleForm
from config import config
from sqlalchemy.exc import IntegrityError
from auth import admin_required
from faculty_auth import faculty_required
from datetime import time, datetime, date, timedelta
import requests

app = Flask(__name__)

# Load configuration
app.config.from_object(config['development'])

# Initialize extensions
db.init_app(app)
Bootstrap5(app)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    form = AdminLoginForm()

    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()

        if admin and admin.check_password(form.password.data):
            session["admin_id"] = admin.id
            session["admin_username"] = admin.username
            flash("Login successful", "success")
            return redirect(url_for("faculty_list"))

        flash("Invalid username or password", "danger")

    return render_template("admin_login.html", form=form)


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    flash("Logged out successfully", "info")
    return redirect(url_for("admin_login"))

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    """Redirect to main admin view"""
    return redirect(url_for("faculty_list"))

@app.route("/faculty/login", methods=["GET", "POST"])
def faculty_login():
    form = FacultyLoginForm()

    if form.validate_on_submit():
        faculty = Faculty.query.filter_by(email=form.email.data).first()

        if not faculty:
            flash("Invalid credentials", "danger")
            return redirect(url_for("faculty_login"))

        # 🔹 FIRST TIME LOGIN
        if faculty.password_hash is None:
            session["reset_faculty_id"] = faculty.id
            return redirect(url_for("faculty_set_password"))

        if faculty.check_password(form.password.data):
            session["faculty_id"] = faculty.id
            session["faculty_name"] = faculty.name
            flash("Welcome!", "success")
            return redirect(url_for("faculty_dashboard"))

        flash("Invalid credentials", "danger")

    return render_template("faculty_login.html", form=form)

@app.route("/faculty/set-password", methods=["GET", "POST"])
def faculty_set_password():
    faculty_id = session.get("reset_faculty_id")

    if not faculty_id:
        return redirect(url_for("faculty_login"))

    faculty = Faculty.query.get_or_404(faculty_id)
    form = FacultySetPasswordForm()

    if form.validate_on_submit():
        faculty.set_password(form.password.data)
        db.session.commit()

        session.pop("reset_faculty_id")
        flash("Password set successfully. Please login.", "success")
        return redirect(url_for("faculty_login"))

    return render_template("faculty_set_password.html", form=form)


@app.route("/faculty/logout")
def faculty_logout():
    session.pop("faculty_id", None)
    session.pop("faculty_name", None)
    flash("Logged out", "info")
    return redirect(url_for("faculty_login"))


@app.route('/')
def index():
    if "admin_id" in session:
        return redirect(url_for('faculty_list'))
    elif "faculty_id" in session:
        return redirect(url_for('faculty_dashboard'))
    return redirect(url_for('admin_login'))




@app.route('/faculty/add', methods=['GET', 'POST'])
@admin_required
def faculty_add():
    """Add new faculty member"""
    form = FacultyForm()

    # Populate dynamic choices
    choices = populate_form_choices()
    form.department.choices = choices['departments']
    form.subjects.choices = choices['subjects']

    if form.validate_on_submit():
        try:
            # Create new faculty
            new_faculty = Faculty(
                name=form.name.data,
                email=form.email.data,
                phone=form.phone.data,
                department_id=form.department.data,
                designation=form.designation.data,
                qualification=form.qualification.data,
                experience_years=form.experience_years.data
            )
            db.session.add(new_faculty)
            db.session.flush()

            if form.subjects.data:
                for subject_id in form.subjects.data:
                    faculty_subject = FacultySubject(
                        faculty_id=new_faculty.id,
                        subject_id=int(subject_id),
                        semester=form.semester.data
                    )
                    db.session.add(faculty_subject)

            db.session.commit()
            flash(f'Faculty "{new_faculty.name}" added successfully!', 'success')
            return redirect(url_for('faculty_list'))

        except IntegrityError:
            db.session.rollback()
            flash('Database error: Email might already exist', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error occurred: {str(e)}', 'danger')

    return render_template('faculty_form.html', form=form, action='Add', faculty=None, choices=choices)


@app.route('/faculty/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def faculty_edit(id):
    """Edit existing faculty member"""
    faculty = Faculty.query.get_or_404(id)
    form = FacultyForm(obj=faculty)
    form.faculty_id = id

    choices = populate_form_choices()
    form.department.choices = choices['departments']
    form.subjects.choices = choices['subjects']

    if request.method == 'GET':
        current_subjects = [fs.subject_id for fs in faculty.subjects]
        form.subjects.data = current_subjects

        if faculty.subjects:
            first_assignment = faculty.subjects[0]
            form.semester.data = first_assignment.semester

    if form.validate_on_submit():
        try:
            faculty.name = form.name.data
            faculty.email = form.email.data
            faculty.phone = form.phone.data
            faculty.department_id = form.department.data
            faculty.designation = form.designation.data
            faculty.qualification = form.qualification.data
            faculty.experience_years = form.experience_years.data

            # Remove old assignments
            FacultySubject.query.filter_by(faculty_id=id).delete()

            # Add new assignments from selected subjects
            if form.subjects.data:
                for subject_id in form.subjects.data:
                    faculty_subject = FacultySubject(
                        faculty_id=faculty.id,
                        subject_id=int(subject_id),
                        semester=form.semester.data
                    )
                    db.session.add(faculty_subject)

            db.session.commit()
            flash(f'Faculty "{faculty.name}" updated successfully!', 'success')
            return redirect(url_for('faculty_list'))

        except IntegrityError:
            db.session.rollback()
            flash('Database error: Email might already exist', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error occurred: {str(e)}', 'danger')

    return render_template('faculty_form.html', form=form, action='Edit', faculty=faculty, choices=choices)


@app.route('/faculty/list')
@admin_required
def faculty_list():
    faculties = Faculty.query.all()
    faculty_data = []
    for faculty in faculties:
        subject_count = len(faculty.subjects)
        faculty_data.append({
            'faculty': faculty,
            'subject_count': subject_count
        })
    return render_template('faculty_list.html', faculty_data=faculty_data)


@app.route('/faculty/view/<int:id>')
@admin_required
def faculty_view(id):
    """View detailed faculty information"""
    faculty = Faculty.query.get_or_404(id)

    # Calculate attendance
    total_days = len(faculty.attendance_records)
    present_days = len([a for a in faculty.attendance_records if a.status == 'Present'])
    attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0

    # Get leaves
    pending_leaves = [l for l in faculty.leaves if l.status == 'Pending']
    approved_leaves = [l for l in faculty.leaves if l.status == 'Approved']

    return render_template('faculty_view.html',
                           faculty=faculty,
                           attendance_percentage=attendance_percentage,
                           pending_leaves=pending_leaves,
                           approved_leaves=approved_leaves)


@app.route('/faculty/delete/<int:id>', methods=['POST'])
@admin_required
def faculty_delete(id):
    """Delete a faculty member"""
    faculty = Faculty.query.get_or_404(id)

    try:
        faculty_name = faculty.name
        db.session.delete(faculty)
        db.session.commit()
        flash(f'Faculty "{faculty_name}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting faculty: {str(e)}', 'danger')

    return redirect(url_for('faculty_list'))



# Master Data Management Consolidated in /admin/academics


@app.route("/faculty/dashboard")
@faculty_required
def faculty_dashboard():
    faculty_id = session["faculty_id"]
    faculty = Faculty.query.get_or_404(faculty_id) # Fetch faculty object

    # Calculate Attendance Stats
    total_days = len(faculty.attendance_records)
    present_days = len([a for a in faculty.attendance_records if a.status == 'Present'])
    attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0

    # Existing Timetable Logic
    slots = (
        Timetable.query
        .filter_by(faculty_id=faculty_id)
        .order_by(Timetable.day, Timetable.start_time)
        .all()
    )

    from collections import defaultdict
    week = defaultdict(list)
    for slot in slots:
        week[slot.day].append(slot)

    return render_template(
        "faculty_dashboard.html",
        week=week,
        attendance_percentage=round(attendance_percentage, 2), # Pass to template
        present_days=present_days,
        total_days=total_days
    )




@app.route("/api/department/<int:dept_id>/data")
@admin_required
def department_data(dept_id):
    faculty = Faculty.query.filter_by(department_id=dept_id).all()

    subjects = (
        Subject.query
        .join(FacultySubject)
        .join(Faculty)
        .filter(Faculty.department_id == dept_id)
        .distinct()
        .all()
    )

    classes = AcademicClass.query.filter_by(department_id=dept_id).all()

    return {
        "faculty": [{"id": f.id, "name": f.name} for f in faculty],
        "subjects": [{"id": s.id, "name": s.subject_name} for s in subjects],
        "classes": [{"id": c.id, "name": c.name} for c in classes],
    }





@app.route("/admin/attendance/save", methods=["POST"])
@admin_required
def save_attendance():
    date_str = request.form.get("date")  # This is a string from the form

    # Convert string 'YYYY-MM-DD' to a Python date object
    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        flash("Invalid date format", "danger")
        return redirect(url_for("faculty_attendance_manage"))

    for key, value in request.form.items():
        if not key.startswith("status_"):
            continue

        faculty_id = int(key.split("_")[1])

        # Check for approved leaves
        existing_leave = FacultyLeave.query.filter(
            FacultyLeave.faculty_id == faculty_id,
            FacultyLeave.status == "Approved",
            FacultyLeave.start_date <= selected_date,
            FacultyLeave.end_date >= selected_date
        ).first()

        if existing_leave:
            # If on leave, force status to 'Leave' or skip
            # Ideally, we warn the user, but for bulk save we might just enforce consistency
            if value == "Present":
                 flash(f"Warning: Faculty {faculty_id} is on approved leave. Marked as 'Leave'.", "warning")
                 value = "Leave"

        # Use the date object for the query and the new record
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
    return redirect(url_for("admin_hr", tab="attendance"))

@app.route("/faculty/attendance")
@faculty_required
def faculty_attendance_view():
    records = FacultyAttendance.query.filter_by(
        faculty_id=session["faculty_id"]
    ).order_by(FacultyAttendance.date.desc()).all()

    return render_template(
        "attendance_view.html",
        records=records
    )

@app.route("/faculty/leave/apply", methods=["GET", "POST"])
@faculty_required
def faculty_apply_leave():
    form = FacultyLeaveForm()
    faculty_id = session["faculty_id"]

    if form.validate_on_submit():
        leave = FacultyLeave(
            faculty_id=faculty_id,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            reason=form.reason.data
        )
        db.session.add(leave)
        db.session.commit()

        flash("Leave request submitted", "success")
        return redirect(url_for("faculty_my_leaves"))

    return render_template("apply_leave.html", form=form)


@app.route("/faculty/leaves")
@faculty_required
def faculty_my_leaves():
    faculty_id = session["faculty_id"]

    leaves = FacultyLeave.query.filter_by(
        faculty_id=faculty_id
    ).order_by(FacultyLeave.applied_at.desc()).all()

    return render_template(
        "my_leaves.html",
        leaves=leaves
    )



@app.route("/admin/leave/<int:leave_id>/approve")
@admin_required
def approve_leave(leave_id):
    leave = FacultyLeave.query.get_or_404(leave_id)

    if leave.status != "Pending":
        flash("Leave already processed", "warning")
        return redirect(url_for("admin_leaves"))

    leave.status = "Approved"
    db.session.commit()

    flash("Leave approved successfully", "success")
    return redirect(url_for("admin_hr", tab="leaves"))


@app.route("/admin/leave/<int:leave_id>/reject")
@admin_required
def reject_leave(leave_id):
    leave = FacultyLeave.query.get_or_404(leave_id)

    if leave.status != "Pending":
        flash("Leave already processed", "warning")
        return redirect(url_for("admin_leaves"))

    leave.status = "Rejected"
    db.session.commit()

    flash("Leave rejected", "danger")
    return redirect(url_for("admin_hr", tab="leaves"))









@app.route("/admin/academics", methods=["GET", "POST"])
@admin_required
def admin_academics():
    """Unified dashboard for Master Data"""
    # Active Tab Logic
    active_tab = request.args.get('tab', 'departments') # Default to departments

    # Forms
    dept_form = DepartmentForm()
    subject_form = SubjectForm()
    class_form = AcademicClassForm()
    room_form = ClassroomForm()

    # Populate choices for Class Form
    class_form.department_id.choices = [
        (d.id, d.name) for d in Department.query.all()
    ]

    # --- HANDLE SUBMISSIONS ---
    # We check which form was submitted based on the active tab or submit button
    
    # 1. Departments
    if active_tab == 'departments' and dept_form.validate_on_submit():
        try:
            department = Department(name=dept_form.name.data.strip())
            db.session.add(department)
            db.session.commit()
            flash("Department added successfully", "success")
            return redirect(url_for("admin_academics", tab='departments'))
        except IntegrityError:
            db.session.rollback()
            flash("Department already exists", "danger")

    # 2. Subjects
    if active_tab == 'subjects' and subject_form.validate_on_submit():
        try:
            subject = Subject(
                subject_code=subject_form.subject_code.data.strip().upper(),
                subject_name=subject_form.subject_name.data.strip()
            )
            db.session.add(subject)
            db.session.commit()
            flash("Subject added successfully", "success")
            return redirect(url_for("admin_academics", tab='subjects'))
        except IntegrityError:
            db.session.rollback()
            flash("Subject code already exists", "danger")

    # 3. Academic Classes
    if active_tab == 'classes' and class_form.validate_on_submit():
        try:
             # Logic from old academic_class_manage
            academic_class = AcademicClass(
                name=class_form.name.data,
                year=class_form.year.data,
                department_id=class_form.department_id.data
            )
            db.session.add(academic_class)
            db.session.commit()
            flash("Academic Class added successfully", "success")
            return redirect(url_for("admin_academics", tab='classes'))
        except IntegrityError:
             db.session.rollback()
             flash("Class name must be unique", "danger")

    # 4. Classrooms
    if active_tab == 'classrooms' and room_form.validate_on_submit():
        try:
            classroom = Classroom(
                room_code=room_form.room_code.data.upper(),
                room_type=room_form.room_type.data,
                capacity=room_form.capacity.data
            )
            db.session.add(classroom)
            db.session.commit()
            flash("Classroom added successfully", "success")
            return redirect(url_for("admin_academics", tab='classrooms'))
        except IntegrityError:
             db.session.rollback()
             flash("Room code already exists", "danger")

    # --- FETCH DATA FOR RENDERING ---
    departments = Department.query.order_by(Department.name).all()
    subjects = Subject.query.order_by(Subject.subject_code).all()
    classes = AcademicClass.query.order_by(AcademicClass.year, AcademicClass.name).all()
    classrooms = Classroom.query.order_by(Classroom.room_code).all()
    
    # --- HANDLE DELETE ---
    if delete_id := request.args.get("delete"):
        delete_id = int(delete_id)
        
        if active_tab == 'departments':
            dept = Department.query.get_or_404(delete_id)
            if dept.academic_classes or dept.faculties:
                flash("Cannot delete Department linked to Classes or Faculty", "danger")
            else:
                db.session.delete(dept)
                db.session.commit()
                flash("Department deleted", "success")
                return redirect(url_for('admin_academics', tab='departments'))

        elif active_tab == 'subjects':
            subj = Subject.query.get_or_404(delete_id)
            if subj.timetables or subj.faculty_allocations:
                 flash("Cannot delete Subject linked to Timetable/Faculty", "danger")
            else:
                db.session.delete(subj)
                db.session.commit()
                flash("Subject deleted", "success")
                return redirect(url_for('admin_academics', tab='subjects'))

        elif active_tab == 'classes':
             cls = AcademicClass.query.get_or_404(delete_id)
             if cls.timetables:
                 flash("Cannot delete Class linked to Timetable", "danger")
             else:
                 db.session.delete(cls)
                 db.session.commit()
                 flash("Academic Class deleted", "success")
                 return redirect(url_for('admin_academics', tab='classes'))

        elif active_tab == 'classrooms':
            room = Classroom.query.get_or_404(delete_id)
            if room.timetables:
                flash("Cannot delete Classroom linked to Timetable", "danger")
            else:
                db.session.delete(room)
                db.session.commit()
                flash("Classroom deleted", "success")
                return redirect(url_for('admin_academics', tab='classrooms'))

    return render_template(
        "admin_academics.html",
        active_tab=active_tab,
        dept_form=dept_form,
        subject_form=subject_form,
        class_form=class_form,
        room_form=room_form,
        departments=departments,
        subjects=subjects,
        classes=classes,
        classrooms=classrooms
    )


    return render_template(
        "admin_academics.html",
        active_tab=active_tab,
        dept_form=dept_form,
        subject_form=subject_form,
        class_form=class_form,
        room_form=room_form,
        departments=departments,
        subjects=subjects,
        classes=classes,
        classrooms=classrooms
    )

@app.route("/admin/schedule", methods=["GET", "POST"])
@admin_required
def admin_schedule():
    """Unified Schedule Center"""
    active_tab = request.args.get('tab', 'manage')
    
    # --- FORMS ---
    manage_form = TimetableForm()
    classroom_form = ClassroomFilterForm()
    daily_form = DailyScheduleForm()

    # Populate choices for Timetable Manage
    manage_form.department_id.choices = [(d.id, d.name) for d in Department.query.all()]
    manage_form.faculty_id.choices = [(f.id, f.name) for f in Faculty.query.all()]
    manage_form.subject_id.choices = [(s.id, s.subject_name) for s in Subject.query.all()]
    manage_form.academic_class_id.choices = [(c.id, c.name) for c in AcademicClass.query.all()]
    manage_form.classroom_id.choices = [(c.id, c.room_code) for c in Classroom.query.all()]
    
    # Populate choices for Classroom Filter
    classroom_form.classroom_id.choices = [(c.id, c.room_code) for c in Classroom.query.order_by(Classroom.room_code).all()]

    # --- DATA & LOGIC ---
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
             # Basic Time Object
            start_dt = datetime.strptime(manage_form.start_time.data, "%H:%M").time()
            end_dt = (datetime.combine(date.today(), start_dt) + timedelta(hours=1)).time()
            
            # Check Faculty Conflict
            if Timetable.query.filter_by(
                day=manage_form.day.data,
                start_time=start_dt,
                faculty_id=manage_form.faculty_id.data
            ).first():
                 flash("Faculty is already booked at this time!", "danger")
                 return redirect(url_for('admin_schedule', tab='manage'))

            # Check Class Conflict
            if Timetable.query.filter_by(
                day=manage_form.day.data,
                start_time=start_dt,
                academic_class_id=manage_form.academic_class_id.data
            ).first():
                 flash("Class is already booked at this time!", "danger")
                 return redirect(url_for('admin_schedule', tab='manage'))

            # Create Slot
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
            return redirect(url_for('admin_schedule', tab='manage'))

        except IntegrityError:
            db.session.rollback()
            flash("Error: Classroom Double Booking Detected!", "danger")
    
    # 2. CLASSROOM TAB
    classroom_grid = {d: {t: None for t in TIMES} for d in DAYS}
    selected_classroom = None
    
    if active_tab == 'classroom' and classroom_form.validate_on_submit():
        c_id = classroom_form.classroom_id.data
        selected_classroom = Classroom.query.get(c_id)
        c_slots = Timetable.query.filter_by(classroom_id=c_id).all()
        for slot in c_slots:
            t = slot.start_time.strftime("%H:%M")
            if t in TIMES:
                classroom_grid[slot.day][t] = slot
    
    # 3. DAILY TAB
    daily_schedule_data = []
    selected_date = date.today()
    day_name = selected_date.strftime("%A")

    if active_tab == 'daily' and daily_form.validate_on_submit():
        selected_date = daily_form.date.data
        day_name = selected_date.strftime("%A")
        
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
        "admin_schedule.html",
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
        times=TIMES
    )


@app.route("/admin/hr", methods=["GET", "POST"])
@admin_required
def admin_hr():
    active_tab = request.args.get('tab', 'attendance')
    
    # --- TAB 1: ATTENDANCE ---
    attendance_form = AdminAttendanceFilterForm()
    attendance_form.department_id.choices = [(d.id, d.name) for d in Department.query.all()]
    
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

    # --- TAB 2: LEAVES ---
    leaves = FacultyLeave.query.order_by(FacultyLeave.applied_at.desc()).all()

    return render_template(
        "admin_faculty_hr.html",
        active_tab=active_tab,
        attendance_form=attendance_form,
        faculty_list=faculty_list,
        existing_attendance=existing_attendance,
        leaves=leaves
    )


@app.cli.command("create-admin")
def create_admin():
    username = input("Admin username: ")
    password = input("Admin password: ")

    if Admin.query.filter_by(username=username).first():
        print("Admin already exists")
        return

    admin = Admin(username=username)
    admin.set_password(password)

    db.session.add(admin)
    db.session.commit()
    print("Admin created successfully")


# --- API ENDPOINTS (React Integration) ---

# Database initialization commands
@app.cli.command()
def init_db():
    """Initialize database with tables"""
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")


@app.cli.command()
def seed_db():
    """Seed database with sample data"""
    # Add departments (only missing ones)
    dept_names = ['Computer Science', 'Electronics', 'Mechanical', 'Civil', 'Mathematics']
    existing_depts = {d.name for d in Department.query.all()}
    if new_departments := [
        Department(name=n) for n in dept_names if n not in existing_depts
    ]:
        db.session.bulk_save_objects(new_departments)
        db.session.commit()

    # Add subjects (only missing ones)
    subject_defs = [
        ('CS101', 'Data Structures'),
        ('CS102', 'Database Management'),
        ('CS103', 'Operating Systems'),
        ('EC101', 'Digital Electronics'),
        ('ME101', 'Thermodynamics'),
        ('MA101', 'Linear Algebra')
    ]
    existing_codes = {s.subject_code for s in Subject.query.all()}
    if new_subjects := [
        Subject(subject_code=code, subject_name=name)
        for code, name in subject_defs
        if code not in existing_codes
    ]:
        db.session.bulk_save_objects(new_subjects)
        db.session.commit()

    print("Database seeded with sample data!")


@app.context_processor
def inject_user_roles():
    return {
        "is_admin": "admin_id" in session,
        "admin_username": session.get("admin_username"),
        "is_faculty": "faculty_id" in session,
        "faculty_name": session.get("faculty_name"),
    }





if __name__ == '__main__':
    app.run(debug=True)
