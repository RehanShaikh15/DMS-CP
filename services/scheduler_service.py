from models import db, Timetable, FacultyLeave, Classroom, Faculty
from datetime import datetime, date, time, timedelta

class ConflictEngine:
    @staticmethod
    def check_conflicts(day, start_time, end_time, faculty_id, academic_class_id, classroom_id, subject_id, semester=None):
        """
        Check for conflicts in:
        1. Faculty Schedule (Time collision)
        2. Academic Class Schedule (Time collision)
        3. Classroom Schedule (Time collision)
        4. Faculty Leave (Warning if on leave)
        """
        conflicts = []

        # 1. Faculty Clash
        faculty_clash = Timetable.query.filter(
            Timetable.day == day,
            Timetable.start_time == start_time,
            Timetable.faculty_id == faculty_id
        ).first()
        if faculty_clash:
            conflicts.append(f"Faculty is already booked in {faculty_clash.classroom.room_code} for {faculty_clash.academic_class.name}.")

        # 2. Academic Class Clash
        class_clash = Timetable.query.filter(
            Timetable.day == day,
            Timetable.start_time == start_time,
            Timetable.academic_class_id == academic_class_id
        ).first()
        if class_clash:
            conflicts.append(f"Class {class_clash.academic_class.name} already has a class in {class_clash.classroom.room_code} with {class_clash.faculty.name}.")

        # 3. Classroom Clash
        room_clash = Timetable.query.filter(
            Timetable.day == day,
            Timetable.start_time == start_time,
            Timetable.classroom_id == classroom_id
        ).first()
        if room_clash:
             conflicts.append(f"Classroom {room_clash.classroom.room_code} is occupied by {room_clash.academic_class.name} ({room_clash.faculty.name}).")
        
        # 4. Faculty Leave Awareness (Warning)
        # Since timetable is generic (Mon-Fri), we warn if there's an ACTIVE leave for this faculty TODAY or generally (future enhancement: check specifically for next occurrence of 'day')
        # For now, let's just check if there is ANY approved leave that overlaps with *current* week or future dates.
        # A simple heuristic: check if faculty has approved leave spanning > 7 days or is currently on leave.
        
        # Actually, let's just check if there is an approved leave active *today*. 
        # But this is a planning tool. So maybe just warn "Faculty has pending/approved leaves: [Dates]"
        today = date.today()
        upcoming_leaves = FacultyLeave.query.filter(
            FacultyLeave.faculty_id == faculty_id,
            FacultyLeave.status == 'Approved',
            FacultyLeave.end_date >= today
        ).all()
        
        if upcoming_leaves:
            leave_strs = [f"{l.start_date} to {l.end_date} ({l.reason})" for l in upcoming_leaves]
            conflicts.append(f"WARNING: Faculty has approved leave(s): {', '.join(leave_strs)}")

        # 5. Faculty Workload Check
        # Check if adding this slot exceeds MAX_WORKLOAD_HOURS
        # We assume 1 slot = 1 hour. Get current workload.
        current_workload = ConflictEngine.get_faculty_workload(faculty_id)
        
        # Import Config to get MAX_WORKLOAD_HOURS (avoid circular import if possible, or use current_app)
        from flask import current_app
        max_hours = current_app.config.get('MAX_WORKLOAD_HOURS', 18)
        
        # If we are in an edit scenario, we might want to exclude the current slot being edited.
        # But here in 'check_conflicts', we usually check before adding a NEW slot.
        # If valid, workload becomes current + 1.
        if current_workload >= max_hours:
             conflicts.append(f"Faculty has reached maximum weekly workload ({current_workload}/{max_hours} hours).")

        return conflicts

    @staticmethod
    def get_faculty_workload(faculty_id):
        """
        Calculate total weekly teaching hours for a faculty.
        Assumes 1 slot = 1 hour (since slots are 09:00-10:00 etc).
        If slots have different durations, we should sum (end_time - start_time).
        """
        slots = Timetable.query.filter_by(faculty_id=faculty_id).all()
        # Simple count for now
        return len(slots)

    @staticmethod
    def find_next_available_slot(faculty_id, academic_class_id, classroom_id, duration_hours=1):
        """
        Find the first available slot (Day, Time) for the given Faculty, Class, and Room.
        Excludes occupied slots.
        """
        DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        TIMES = [
            time(9, 0), time(10, 0), time(11, 0), time(12, 0), 
            time(14, 0), time(15, 0)
        ] # Based on admin_routes.py

        for d in DAYS:
            for t in TIMES:
                # Check for conflicts manually for this slot
                # (We can optimize this by querying all slots for these entities once, but loop is fine for small scale)
                
                # Check Faculty
                if Timetable.query.filter_by(day=d, start_time=t, faculty_id=faculty_id).first():
                    continue
                
                # Check Class
                if Timetable.query.filter_by(day=d, start_time=t, academic_class_id=academic_class_id).first():
                    continue

                # Check Room
                if Timetable.query.filter_by(day=d, start_time=t, classroom_id=classroom_id).first():
                    continue
                
                # If we reach here, it's free!
                return d, t.strftime("%H:%M")
        
        return None, None
