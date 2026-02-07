from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, Text, ForeignKey, DateTime, func, UniqueConstraint, Date, Time
from typing import List
from datetime import datetime, time, date
from werkzeug.security import generate_password_hash, check_password_hash



class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class Admin(db.Model):
    __tablename__ = "admin"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<Admin {self.username}>"

class Department(db.Model):
    """Department table"""
    __tablename__ = 'department'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)

    # Relationship
    faculties: Mapped[List["Faculty"]] = relationship(
        back_populates="department"
    )

    academic_classes: Mapped[list["AcademicClass"]] = relationship(
        back_populates="department"
    )

    def __repr__(self):
        return f'<Department {self.name}>'

class Subject(db.Model):
    """Subject table"""
    __tablename__ = 'subject'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subject_code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    subject_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    #Relationships
    faculty_assignments: Mapped[List["FacultySubject"]] = relationship(back_populates="subject", cascade="all, delete-orphan")

    timetable_slots: Mapped[List["Timetable"]] = relationship(
        back_populates="subject",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f'<Subject {self.subject_code}: {self.subject_name}>'

class Faculty(db.Model):
    """Faculty table - main entity"""
    __tablename__ = 'faculty'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(10), nullable=False)
    department_id: Mapped[int] = mapped_column(ForeignKey("department.id"),nullable=False)
    designation: Mapped[str] = mapped_column(String(50), nullable=False)
    qualification: Mapped[str] = mapped_column(String(100), nullable=False)
    experience_years: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime,server_default=func.now())
    # Relationships
    department: Mapped["Department"] = relationship(back_populates="faculties")

    subjects: Mapped[List["FacultySubject"]] = relationship(
        back_populates="faculty",
        cascade="all, delete-orphan"
    )
    leaves: Mapped[List["FacultyLeave"]] = relationship(
        back_populates="faculty",
        cascade="all, delete-orphan"
    )
    timetables: Mapped[List["Timetable"]] = relationship(
        back_populates="faculty",
        cascade="all, delete-orphan"
    )
    attendance_records: Mapped[list["FacultyAttendance"]] = relationship(
        back_populates="faculty",
        cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def __repr__(self):
        return f'<Faculty {self.name}>'

# models.py
class FacultySubject(db.Model):
    """Faculty-Subject mapping table"""
    __tablename__ = 'faculty_subject'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    faculty_id: Mapped[int] = mapped_column(ForeignKey("faculty.id"), nullable=False)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subject.id"), nullable=False)
    semester: Mapped[str] = mapped_column(String(20), nullable=False)
    # [cite_start]weekly_hours field has been removed [cite: 12]

    faculty: Mapped["Faculty"] = relationship(back_populates="subjects")
    subject: Mapped["Subject"] = relationship(back_populates="faculty_assignments")

    __table_args__ = (
        UniqueConstraint(
            "faculty_id",
            "subject_id",
            "semester",
            name="unique_faculty_subject_semester"
        ),
    )

    def __repr__(self):
        return f'<FacultySubject Faculty:{self.faculty_id} Subject:{self.subject_id}>'


class FacultyAttendance(db.Model):
    __tablename__ = "faculty_attendance"

    id: Mapped[int] = mapped_column(primary_key=True)

    faculty_id: Mapped[int] = mapped_column(
        ForeignKey("faculty.id"), nullable=False
    )

    date: Mapped[date] = mapped_column(Date, nullable=False)

    status: Mapped[str] = mapped_column(
        String(10), nullable=False
    )  # Present / Absent / Leave

    marked_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    faculty: Mapped["Faculty"] = relationship(
        back_populates="attendance_records"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "faculty_id", "date",
            name="uq_faculty_attendance_day"
        ),
    )



from datetime import date, datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Date, DateTime, String, ForeignKey

class FacultyLeave(db.Model):
    __tablename__ = "faculty_leave"

    id: Mapped[int] = mapped_column(primary_key=True)

    faculty_id: Mapped[int] = mapped_column(
        ForeignKey("faculty.id"), nullable=False
    )

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)

    reason: Mapped[str] = mapped_column(String(255), nullable=False)

    status: Mapped[str] = mapped_column(
        String(20), default="Pending", nullable=False
    )
    # Pending | Approved | Rejected

    applied_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    faculty = relationship("Faculty", back_populates="leaves")


class Timetable(db.Model):
    __tablename__ = "timetable"

    id: Mapped[int] = mapped_column(primary_key=True)

    faculty_id: Mapped[int] = mapped_column(
        ForeignKey("faculty.id"), nullable=False
    )

    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subject.id"), nullable=False
    )

    academic_class_id: Mapped[int] = mapped_column(
        ForeignKey("academic_class.id"), nullable=False
    )
    classroom_id: Mapped[int] = mapped_column(ForeignKey("classroom.id"))


    day: Mapped[str] = mapped_column(String(10), nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)

    faculty: Mapped["Faculty"] = relationship(
        back_populates="timetables"
    )

    subject: Mapped["Subject"] = relationship(
        back_populates="timetable_slots"
    )

    academic_class: Mapped["AcademicClass"] = relationship(
        back_populates="timetables"
    )
    classroom: Mapped["Classroom"] = relationship(back_populates="timetables")


    __table_args__ = (
        db.UniqueConstraint(
            "day",
            "start_time",
            "faculty_id",
            name="uq_faculty_slot"
        ),
        db.UniqueConstraint(
            "day",
            "start_time",
            "academic_class_id",
            name="uq_class_slot"
        ),
        db.UniqueConstraint(
            "day",
            "start_time",
            "classroom_id",
            name="uq_classroom_slot"
        ),
    )


class AcademicClass(db.Model):
    __tablename__ = "academic_class"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    year: Mapped[int] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    department_id: Mapped[int] = mapped_column(
        ForeignKey("department.id"),
        nullable=False
    )

    department: Mapped["Department"] = relationship(back_populates="academic_classes")

    timetables: Mapped[list["Timetable"]] = relationship(
        back_populates="academic_class",
        cascade="all, delete-orphan"
    )

class Classroom(db.Model):
    __tablename__ = "classroom"

    id: Mapped[int] = mapped_column(primary_key=True)

    room_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    room_type: Mapped[str] = mapped_column(String(20), nullable=False)  # Lab / Lecture / Seminar
    capacity: Mapped[int] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    timetables: Mapped[list["Timetable"]] = relationship(
        back_populates="classroom",
        cascade="all, delete"
    )

    def __repr__(self):
        return f"<Classroom {self.room_code}>"


class AcademicCalendar(db.Model):
    """Academic Calendar table"""
    __tablename__ = 'academic_calendar'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[date] = mapped_column(Date, unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    is_holiday: Mapped[bool] = mapped_column(default=False)
    is_exam: Mapped[bool] = mapped_column(default=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False) # Holiday, Exam, Event

    def __repr__(self):
        return f'<Calendar {self.date}: {self.description}>'

