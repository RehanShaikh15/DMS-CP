from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SelectField, IntegerField, TextAreaField, TimeField, SubmitField, SelectMultipleField, PasswordField, DateField
from wtforms.validators import DataRequired, Email, Length, NumberRange, ValidationError, Optional, EqualTo
from models import Faculty, Department, Subject
import re
from datetime import date


class AdminLoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class FacultyLoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class FacultySetPasswordForm(FlaskForm):
    password = PasswordField(
        "New Password",
        validators=[DataRequired(), Length(min=6)]
    )
    confirm = PasswordField(
        "Confirm Password",
        validators=[EqualTo("password")]
    )
    submit = SubmitField("Set Password")

class FacultyForm(FlaskForm):
    """Faculty Management Form"""

    # SECTION 1: BASIC INFORMATION
    name = StringField(
        'Full Name',
        validators=[
            DataRequired(message='Name is required'),
            Length(min=3, max=100, message='Name must be between 3 and 100 characters')
        ],
        render_kw={'placeholder': 'Enter full name', 'class': 'form-control'}
    )

    email = EmailField(
        'Email Address',
        validators=[
            DataRequired(message='Email is required'),
            Email(message='Invalid email format')
        ],
        render_kw={'placeholder': 'faculty@college.edu', 'class': 'form-control'}
    )

    phone = StringField(
        'Phone Number',
        validators=[
            DataRequired(message='Phone number is required'),
            Length(min=10, max=10, message='Phone number must be exactly 10 digits')
        ],
        render_kw={'placeholder': '9876543210', 'class': 'form-control', 'maxlength': '10'}
    )

    # SECTION 2: ACADEMIC DETAILS
    department = SelectField(
        'Department',
        coerce=int,
        validators=[DataRequired(message='Please select a department')],
        render_kw={'class': 'form-select'}
    )

    designation = SelectField(
        'Designation',
        choices=[
            ('', 'Select Designation'),
            ('Assistant Professor', 'Assistant Professor'),
            ('Associate Professor', 'Associate Professor'),
            ('Professor', 'Professor')
        ],
        validators=[DataRequired(message='Please select a designation')],
        render_kw={'class': 'form-select'}
    )

    qualification = StringField(
        'Highest Qualification',
        validators=[
            DataRequired(message='Qualification is required'),
            Length(min=2, max=100, message='Qualification must be between 2 and 100 characters')
        ],
        render_kw={'placeholder': 'Ph.D., M.Tech, etc.', 'class': 'form-control'}
    )

    experience_years = IntegerField(
        'Years of Experience',
        validators=[
            DataRequired(message='Experience is required'),
            NumberRange(min=0, max=50, message='Experience must be between 0 and 50 years')
        ],
        render_kw={'placeholder': '0', 'class': 'form-control', 'min': '0'}
    )

    # SECTION 3: SUBJECT ALLOCATION
    subjects = SelectMultipleField(
        'Subjects',
        coerce=int,  # FIX: Convert checkbox string values to integers
        validators=[Optional()],
        render_kw={'class': 'form-check-input', 'multiple': True}
    )

    semester = SelectField(
        'Semester',
        choices=[
            ('', 'Select Semester'),
            ('1', 'Semester 1'),
            ('2', 'Semester 2'),
            ('3', 'Semester 3'),
            ('4', 'Semester 4'),
            ('5', 'Semester 5'),
            ('6', 'Semester 6'),
            ('7', 'Semester 7'),
            ('8', 'Semester 8')
        ],
        validators=[Optional()],
        render_kw={'class': 'form-select'}
    )


    submit = SubmitField('Save Faculty', render_kw={'class': 'btn btn-primary'})

    # CUSTOM VALIDATORS
    def validate_phone(self, field):
        """Validate phone number format"""
        if not re.match(r'^\d{10}$', field.data):
            raise ValidationError('Phone number must contain exactly 10 digits')

    def validate_email(self, field):
        """Check email uniqueness"""
        faculty_id = getattr(self, 'faculty_id', None)
        if existing_faculty := Faculty.query.filter_by(email=field.data).first():
            if faculty_id is None or existing_faculty.id != faculty_id:
                raise ValidationError('This email is already registered')

    def validate_subjects(self, field):
        """Validate subjects checkbox list - require semester when subjects are selected"""
        if field.data and len(field.data) > 0 and not self.semester.data:
            raise ValidationError('Please select semester when assigning subjects')

class DepartmentForm(FlaskForm):
    name = StringField(
        "Department Name",
        validators=[DataRequired(), Length(max=100)]
    )
    submit = SubmitField("Add Department")

class SubjectForm(FlaskForm):
    subject_code = StringField(
        "Subject Code",
        validators=[DataRequired(), Length(max=20)]
    )
    subject_name = StringField(
        "Subject Name",
        validators=[DataRequired(), Length(max=100)]
    )
    submit = SubmitField("Add Subject")

class AcademicClassForm(FlaskForm):
    name = StringField(
        "Class Name",
        validators=[DataRequired()]
    )

    year = SelectField(
        "Year",
        choices=[
            (1, "FY"),
            (2, "SY"),
            (3, "TY")
        ],
        coerce=int,
        validators=[DataRequired()]
    )

    department_id = SelectField(
        "Department",
        coerce=int,
        validators=[DataRequired()]
    )

    submit = SubmitField("Add Class")

class TimetableForm(FlaskForm):
    department_id = SelectField("Department", coerce=int, validate_choice=False)
    faculty_id = SelectField("Faculty", coerce=int)
    subject_id = SelectField("Subject", coerce=int)
    academic_class_id = SelectField("Academic Class", coerce=int)
    classroom_id = SelectField("Classroom", coerce=int)


    day = SelectField(
        "Day",
        choices=[
            ("Monday", "Monday"),
            ("Tuesday", "Tuesday"),
            ("Wednesday", "Wednesday"),
            ("Thursday", "Thursday"),
            ("Friday", "Friday"),
        ],
    )

    start_time = SelectField(
        "Start Time",
        choices=[
            ("09:00", "09:00"),
            ("10:00", "10:00"),
            ("11:00", "11:00"),
            ("12:00", "12:00"),
            ("14:00", "14:00"),
            ("15:00", "15:00"),
        ],
    )

    submit = SubmitField("Add Slot")

class AdminAttendanceFilterForm(FlaskForm):
    department_id = SelectField(
        "Department", coerce=int, validators=[DataRequired()]
    )
    date = DateField(
        "Date", default=date.today, validators=[DataRequired()]
    )
    submit = SubmitField("Load Faculty")

class FacultyLeaveForm(FlaskForm):
    start_date = DateField(
        "From Date", format="%Y-%m-%d", validators=[DataRequired()]
    )
    end_date = DateField(
        "To Date", format="%Y-%m-%d", validators=[DataRequired()]
    )
    reason = TextAreaField(
        "Reason", validators=[DataRequired()]
    )
    submit = SubmitField("Apply Leave")


class ClassroomForm(FlaskForm):
    room_code = StringField(
        "Room Code",
        validators=[DataRequired()]
    )

    room_type = SelectField(
        "Room Type",
        choices=[
            ("Lecture", "Lecture Hall"),
            ("Lab", "Laboratory"),
            ("Seminar", "Seminar Room")
        ],
        validators=[DataRequired()]
    )

    capacity = IntegerField(
        "Capacity",
        validators=[DataRequired()]
    )

    submit = SubmitField("Save Classroom")

class ClassroomFilterForm(FlaskForm):
    classroom_id = SelectField(
        "Select Classroom",
        coerce=int,
        validators=[DataRequired()]
    )
    submit = SubmitField("View Timetable")

class DailyScheduleForm(FlaskForm):
    date = DateField(
        "Select Date",
        default=date.today,
        validators=[DataRequired()]
    )
    submit = SubmitField("View Schedule")

class AcademicCalendarForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired(), Length(max=200)])
    type = SelectField('Type', choices=[
        ('Holiday', 'Holiday'),
        ('Exam', 'Exam'),
        ('Event', 'Other Event')
    ], validators=[DataRequired()])
    submit = SubmitField('Add Event')

def populate_form_choices():
    """Helper function to populate dynamic choices"""
    departments = Department.query.all()
    department_choices = [(0, 'Select Department')] + [(dept.id, dept.name) for dept in departments]

    subjects = Subject.query.all()
    subject_choices = [(subj.id, f"{subj.subject_code} - {subj.subject_name}") for subj in subjects]

    return {
        'departments': department_choices,
        'subjects': subject_choices
    }