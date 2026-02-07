from flask import render_template, redirect, url_for, flash, request, jsonify
from . import admin_bp
from models import db, Department, Subject, AcademicClass, Classroom
from forms import DepartmentForm, SubjectForm, AcademicClassForm, ClassroomForm
from auth import admin_required
from sqlalchemy.exc import IntegrityError

@admin_bp.route("/admin/academics", methods=["GET", "POST"])
@admin_required
def admin_academics():
    """Unified dashboard for Master Data"""
    # Active tab management
    active_tab = request.args.get('tab', 'departments')
    
    # Initialize all forms
    dept_form = DepartmentForm()
    subject_form = SubjectForm()
    class_form = AcademicClassForm()
    room_form = ClassroomForm()

    # Populate dropdowns for Academic Class Form
    class_form.department_id.choices = [(d.id, d.name) for d in Department.query.order_by(Department.name).all()]

    # ---------------- HANDLE FORM SUBMISSIONS ---------------- #
    
    # 1. DEPARTMENT
    if active_tab == 'departments' and 'submit' in request.form and dept_form.validate_on_submit():
        try:
            db.session.add(Department(name=dept_form.name.data))
            db.session.commit()
            flash("Department added successfully", "success")
            return redirect(url_for('admin.admin_academics', tab='departments'))
        except IntegrityError:
            db.session.rollback()
            flash("Department already exists", "danger")

    # 2. SUBJECT
    elif active_tab == 'subjects' and 'submit' in request.form and subject_form.validate_on_submit():
        try:
            db.session.add(Subject(
                subject_code=subject_form.subject_code.data,
                subject_name=subject_form.subject_name.data
            ))
            db.session.commit()
            flash("Subject added successfully", "success")
            return redirect(url_for('admin.admin_academics', tab='subjects'))
        except IntegrityError:
            db.session.rollback()
            flash("Subject Code already exists", "danger")

    # 3. ACADEMIC CLASS
    elif active_tab == 'classes' and 'submit' in request.form and class_form.validate_on_submit():
        try:
            db.session.add(AcademicClass(
                name=class_form.name.data,
                year=class_form.year.data,
                department_id=class_form.department_id.data
            ))
            db.session.commit()
            flash("Class added successfully", "success")
            return redirect(url_for('admin.admin_academics', tab='classes'))
        except IntegrityError:
            db.session.rollback()
            flash("Class already exists", "danger")

    # 4. CLASSROOM
    elif active_tab == 'classrooms' and 'submit' in request.form and room_form.validate_on_submit():
        try:
            db.session.add(Classroom(
                room_code=room_form.room_code.data,
                room_type=room_form.room_type.data,
                capacity=room_form.capacity.data
            ))
            db.session.commit()
            flash("Classroom added successfully", "success")
            return redirect(url_for('admin.admin_academics', tab='classrooms'))
        except IntegrityError:
            db.session.rollback()
            flash("Room Code must be unique", "danger")


    # HANDLE DELETE ACTION (QUERY PARAMETER)
    if delete_id := request.args.get('delete'):
        try:
            delete_id = int(delete_id)
            if active_tab == 'departments':
                dept = Department.query.get_or_404(delete_id)
                if dept.academic_classes or dept.faculties:
                    # Check if they are active? 
                    # For safety, basic check is fine.
                    flash("Cannot delete Department linked to Classes or Faculty", "danger")
                else:
                    dept.is_active = False
                    db.session.commit()
                    flash("Department archived", "success")
            
            elif active_tab == 'subjects':
                sub = Subject.query.get_or_404(delete_id)
                sub.is_active = False
                db.session.commit()
                flash("Subject archived", "success")

            elif active_tab == 'classes':
                cls = AcademicClass.query.get_or_404(delete_id)
                cls.is_active = False
                db.session.commit()
                flash("Class archived", "success")

            elif active_tab == 'classrooms':
                room = Classroom.query.get_or_404(delete_id)
                room.is_active = False
                db.session.commit()
                flash("Classroom archived", "success")
                
            return redirect(url_for('admin.admin_academics', tab=active_tab))
            
        except ValueError:
            flash("Invalid ID", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"Error during deletion: {str(e)}", "danger")

    departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
    subjects = Subject.query.filter_by(is_active=True).order_by(Subject.subject_code).all()
    classes = AcademicClass.query.filter_by(is_active=True).order_by(AcademicClass.year, AcademicClass.name).all()
    classrooms = Classroom.query.filter_by(is_active=True).order_by(Classroom.room_code).all()

    return render_template(
        "admin/admin_academics.html",
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

@admin_bp.route("/admin/academics/archived")
@admin_required
def admin_academics_archived():
    active_tab = request.args.get('tab', 'departments')
    
    departments = Department.query.filter_by(is_active=False).order_by(Department.name).all()
    subjects = Subject.query.filter_by(is_active=False).order_by(Subject.subject_code).all()
    classes = AcademicClass.query.filter_by(is_active=False).order_by(AcademicClass.year, AcademicClass.name).all()
    classrooms = Classroom.query.filter_by(is_active=False).order_by(Classroom.room_code).all()

    # Reuse admin_academics.html but with is_archived flag
    # We need to pass the forms too, even if not used, or make template robust
    
    # Just pass empty forms as we won't submit them here (or maybe disable them)
    return render_template(
        "admin/admin_academics.html",
        active_tab=active_tab,
        form=None, # Template might need adjustment
        departments=departments,
        subjects=subjects,
        classes=classes,
        classrooms=classrooms,
        is_archived=True,
        # Pass forms to avoid template errors if they are rendered unconditionally
        dept_form=DepartmentForm(),
        subject_form=SubjectForm(),
        class_form=AcademicClassForm(),
        room_form=ClassroomForm()
    )

@admin_bp.route('/admin/restore/<string:type>/<int:id>', methods=['POST'])
@admin_required
def restore_academic(type, id):
    try:
        obj = None
        if type == 'department':
            obj = Department.query.get_or_404(id)
        elif type == 'subject':
            obj = Subject.query.get_or_404(id)
        elif type == 'class':
            obj = AcademicClass.query.get_or_404(id)
        elif type == 'classroom':
            obj = Classroom.query.get_or_404(id)
        
        if obj:
            obj.is_active = True
            db.session.commit()
            flash(f"{type.title()} restored successfully.", "success")
        else:
            flash("Invalid type or ID", "danger")

    except Exception as e:
        db.session.rollback()
        flash(f"Error restoring: {str(e)}", "danger")

    # Return to the correct tab in archived view
    tab_map = {
        'department': 'departments',
        'subject': 'subjects',
        'class': 'classes',
        'classroom': 'classrooms'
    }
    return redirect(url_for('admin.admin_academics_archived', tab=tab_map.get(type, 'departments')))

# Helper for Dynamic Dropdowns (Maybe better in a common util or keep here if specific to academics/schedule)
# But get_faculty_subjects is used by schedule, department_data is used by schedule forms?
# department_data is JSON API.

@admin_bp.route('/api/department/<int:dept_id>/data')
@admin_required
def department_data(dept_id):
    """Get classes and faculty for a department (JSON for dynamic dropdowns)"""
    classes = AcademicClass.query.filter_by(
        department_id=dept_id, 
        is_active=True
    ).order_by(AcademicClass.year, AcademicClass.name).all()
    
    faculty = Faculty.query.filter_by(
        department_id=dept_id,
        is_active=True
    ).order_by(Faculty.name).all()
    
    return jsonify({
        'classes': [{'id': c.id, 'name': f"{c.name} (Year {c.year})"} for c in classes],
        'faculty': [{'id': f.id, 'name': f.name} for f in faculty]
    })
