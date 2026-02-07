from flask import render_template, redirect, url_for, flash, request
from . import admin_bp
from models import db, Faculty, Department, Subject, FacultySubject, Timetable
from forms import FacultyForm, populate_form_choices
from auth import admin_required
from sqlalchemy.exc import IntegrityError

@admin_bp.route('/faculty/list')
@admin_required
def faculty_list():
    faculties = Faculty.query.filter_by(is_active=True).all()
    faculty_data = []
    for faculty in faculties:
        workload_hours = len(faculty.timetables)
        
        status = "Normal"
        if workload_hours > 18:
            status = "Overloaded"
        elif workload_hours < 10:
            status = "Underutilized"

        subject_count = len(faculty.subjects)
        faculty_data.append({
            'faculty': faculty,
            'subject_count': subject_count,
            'workload': workload_hours,
            'status': status
        })
    return render_template('admin/faculty_list.html', faculty_data=faculty_data)

@admin_bp.route('/faculty/archived')
@admin_required
def faculty_archived():
    faculties = Faculty.query.filter_by(is_active=False).all()
    faculty_data = []
    for faculty in faculties:
        workload_hours = len(faculty.timetables)
        subject_count = len(faculty.subjects)
        faculty_data.append({
            'faculty': faculty,
            'subject_count': subject_count,
            'workload': workload_hours,
            'status': "Archived"
        })
    return render_template('admin/faculty_list.html', faculty_data=faculty_data, is_archived=True)

@admin_bp.route('/faculty/restore/<int:id>', methods=['POST'])
@admin_required
def faculty_restore(id):
    faculty = Faculty.query.get_or_404(id)
    try:
        faculty.is_active = True
        db.session.commit()
        flash(f'Faculty "{faculty.name}" restored successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error restoring faculty: {str(e)}', 'danger')
    return redirect(url_for('admin.faculty_archived'))

@admin_bp.route('/faculty/add', methods=['GET', 'POST'])
@admin_required
def faculty_add():
    """Add new faculty member"""
    form = FacultyForm()

    choices = populate_form_choices()
    form.department.choices = choices['departments']
    form.subjects.choices = choices['subjects']

    if form.validate_on_submit():
        try:
            new_faculty = Faculty(
                name=form.name.data,
                email=form.email.data,
                phone=form.phone.data,
                department_id=form.department.data,
                designation=form.designation.data,
                qualification=form.qualification.data,
                experience_years=form.experience_years.data
            )
            # Default password logic inside model or set here? 
            # Controller had new_faculty.set_password(form.password.data) if form has password field?
            # FacultyForm definition in forms.py does NOT have password field for Admin add?
            # Wait, looking at `FacultyForm` in forms.py (lines 30-125), I don't see a password field!
            # But `faculty_add` in `admin_routes.py` didn't set password?
            # Let me check `admin_routes.py` lines 85-93 again in previous `view_file`.
            # It just created Faculty object. It relies on model default or nullable?
            # Model `Faculty` definition? 
            # Ah, `Faculty` model probably generates default password if not provided or it's set elsewhere.
            # In `admin_routes.py` I saw:
            # new_faculty = Faculty(...)
            # db.session.add(new_faculty)
            # It did NOT set password explicitly in the snippet I saw (lines 85-93).
            # So I will follow that.
            
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
            return redirect(url_for('admin.faculty_list'))

        except IntegrityError:
            db.session.rollback()
            flash('Database error: Email might already exist', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error occurred: {str(e)}', 'danger')

    return render_template('admin/faculty_form.html', form=form, action='Add', faculty=None, choices=choices)

@admin_bp.route('/faculty/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def faculty_edit(id):
    """Edit existing faculty member"""
    faculty = Faculty.query.get_or_404(id)
    form = FacultyForm(obj=faculty)
    form.faculty_id = id # For validation

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

            # Add new assignments
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
            return redirect(url_for('admin.faculty_list'))

        except IntegrityError:
            db.session.rollback()
            flash('Database error: Email might already exist', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error occurred: {str(e)}', 'danger')

    return render_template('admin/faculty_form.html', form=form, action='Edit', faculty=faculty, choices=choices)

@admin_bp.route('/faculty/view/<int:id>')
@admin_required
def faculty_view(id):
    """View detailed faculty information"""
    faculty = Faculty.query.get_or_404(id)

    total_days = len(faculty.attendance_records)
    present_days = len([a for a in faculty.attendance_records if a.status == 'Present'])
    attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0

    pending_leaves = [l for l in faculty.leaves if l.status == 'Pending']
    approved_leaves = [l for l in faculty.leaves if l.status == 'Approved']

    return render_template('admin/faculty_view.html',
                           faculty=faculty,
                           attendance_percentage=attendance_percentage,
                           pending_leaves=pending_leaves,
                           approved_leaves=approved_leaves)

@admin_bp.route('/faculty/delete/<int:id>', methods=['POST'])
@admin_required
def faculty_delete(id):
    """Delete a faculty member"""
    faculty = Faculty.query.get_or_404(id)

    try:
        faculty_name = faculty.name
        # Soft Delete
        faculty.is_active = False
        db.session.commit()
        flash(f'Faculty "{faculty_name}" archived successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting faculty: {str(e)}', 'danger')

    return redirect(url_for('admin.faculty_list'))
