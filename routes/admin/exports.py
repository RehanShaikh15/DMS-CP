from flask import render_template, make_response
from . import admin_bp
from models import Faculty, Timetable, FacultyAttendance
from utils.pdf_generator import render_pdf
from services.scheduler_service import ConflictEngine
from auth import admin_required
from datetime import datetime, date, timedelta
import pandas as pd
from io import BytesIO

@admin_bp.route('/export/pdf/timetable/<int:faculty_id>')
@admin_required
def export_timetable_pdf(faculty_id):
    faculty = Faculty.query.get_or_404(faculty_id)
    timetable = Timetable.query.filter_by(faculty_id=faculty_id).order_by(Timetable.day, Timetable.start_time).all()
    
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return render_pdf('reports/pdf_timetable.html', {
        'faculty': faculty,
        'timetable': timetable,
        'generated_at': generated_at
    }, filename=f'timetable_{faculty.name}.pdf')

@admin_bp.route('/export/pdf/attendance/<int:faculty_id>')
@admin_required
def export_attendance_pdf(faculty_id):
    faculty = Faculty.query.get_or_404(faculty_id)
    
    # Get last 30 days
    today = date.today()
    thirty_days_ago = today - timedelta(days=30)
    
    attendance_records = FacultyAttendance.query.filter(
        FacultyAttendance.faculty_id == faculty_id,
        FacultyAttendance.date >= thirty_days_ago
    ).order_by(FacultyAttendance.date.desc()).all()
    
    stats = {
        'present': FacultyAttendance.query.filter_by(faculty_id=faculty_id, status='Present').count(),
        'absent': FacultyAttendance.query.filter_by(faculty_id=faculty_id, status='Absent').count(),
        'leave': FacultyAttendance.query.filter_by(faculty_id=faculty_id, status='Leave').count()
    }
    
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return render_pdf('reports/pdf_attendance.html', {
        'faculty': faculty,
        'attendance_records': attendance_records,
        'stats': stats,
        'generated_at': generated_at
    }, filename=f'attendance_{faculty.name}.pdf')

@admin_bp.route('/export/pdf/profile/<int:faculty_id>')
@admin_required
def export_profile_pdf(faculty_id):
    faculty = Faculty.query.get_or_404(faculty_id)
    workload = ConflictEngine.get_faculty_workload(faculty_id)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return render_pdf('reports/pdf_profile.html', {
        'faculty': faculty,
        'workload': workload,
        'generated_at': generated_at
    }, filename=f'profile_{faculty.name}.pdf')

@admin_bp.route('/export/excel/report')
@admin_bp.route('/export/excel/full_report')
@admin_required
def export_excel_report():
    # Only export active faculty
    faculties = Faculty.query.filter_by(is_active=True).all()
    
    data = []
    for f in faculties:
        workload = ConflictEngine.get_faculty_workload(f.id)
        data.append({
            'ID': f.id,
            'Name': f.name,
            'Email': f.email,
            'Department': f.department.name if f.department else 'N/A',
            'Designation': f.designation,
            'Experience': f.experience_years,
            'Workload (Hrs)': workload,
            'Status': 'Overloaded' if workload > 18 else ('Underutilized' if workload < 10 else 'Normal')
        })
        
    df = pd.DataFrame(data)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Faculty Report')
        
    output.seek(0)
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = 'attachment; filename=faculty_report.xlsx'
    
    return response
