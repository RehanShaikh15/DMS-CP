from flask import render_template
from . import admin_bp
from models import Faculty, Department, Subject, AcademicClass, Classroom, Timetable, FacultyLeave
from auth import admin_required

@admin_bp.route("/admin/analytics")
@admin_required
def analytics():
    """Admin Analytics Dashboard"""
    # 1. Key Metrics
    total_faculty = Faculty.query.filter_by(is_active=True).count()
    total_departments = Department.query.filter_by(is_active=True).count()
    total_subjects = Subject.query.filter_by(is_active=True).count()
    total_classes = AcademicClass.query.filter_by(is_active=True).count()
    total_classrooms = Classroom.query.filter_by(is_active=True).count()

    # 2. Faculty Distribution by Department
    departments = Department.query.filter_by(is_active=True).all()
    dept_labels = [d.name for d in departments]
    dept_data = [len(d.faculties) for d in departments]

    # 3. Faculty Workload (Top 5 Overloaded)
    faculties = Faculty.query.filter_by(is_active=True).all()
    workload_data = []
    for f in faculties:
        hours = len(f.timetables)
        workload_data.append({'name': f.name, 'hours': hours})
    
    # Sort by hours desc and take top 5
    workload_data.sort(key=lambda x: x['hours'], reverse=True)
    top_workload = workload_data[:5]
    
    workload_labels = [w['name'] for w in top_workload]
    workload_values = [w['hours'] for w in top_workload]

    # 4. Leave Statistics (Approved vs Rejected vs Pending)
    pending_leaves = FacultyLeave.query.filter_by(status='Pending').count()
    approved_leaves = FacultyLeave.query.filter_by(status='Approved').count()
    rejected_leaves = FacultyLeave.query.filter_by(status='Rejected').count()

    return render_template(
        "admin/analytics.html",
        total_faculty=total_faculty,
        total_departments=total_departments,
        total_subjects=total_subjects,
        total_classes=total_classes,
        total_classrooms=total_classrooms,
        dept_labels=dept_labels,
        dept_data=dept_data,
        workload_labels=workload_labels,
        workload_values=workload_values,
        pending_leaves=pending_leaves,
        approved_leaves=approved_leaves,
        rejected_leaves=rejected_leaves
    )
