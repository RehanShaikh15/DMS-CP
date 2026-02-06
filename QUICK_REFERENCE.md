# Faculty Management System - Quick Reference

## 🚀 Quick Start (3 Steps)

### Linux/Mac:
```bash
./setup.sh
python app.py
```

### Windows:
```cmd
setup.bat
python app.py
```

### Manual Setup:
```bash
pip install -r requirements.txt
flask --app app init-db
flask --app app seed-db
python app.py
```

## 📋 Common Commands

### Database Management
```bash
# Initialize database
flask --app app init-db

# Seed with sample data
flask --app app seed-db

# Reset database (delete and recreate)
rm college.db
flask --app app init-db
flask --app app seed-db
```

### Running the App
```bash
# Development mode (with auto-reload)
python app.py

# Using Flask CLI
flask --app app run --debug

# Different port
flask --app app run --port 5001

# Accessible from network
flask --app app run --host 0.0.0.0
```

### Testing
```bash
# Run verification tests
python verify.py

# Check if running
curl http://127.0.0.1:5000/

# Test with browser
# Open: http://127.0.0.1:5000
```

## 🔧 Troubleshooting Quick Fixes

### Problem: Port already in use
```bash
# Find process using port 5000
lsof -i :5000  # Linux/Mac
netstat -ano | findstr :5000  # Windows

# Kill the process or use different port
flask --app app run --port 5001
```

### Problem: Module not found
```bash
pip install -r requirements.txt
```

### Problem: Database errors
```bash
rm college.db
flask --app app init-db
flask --app app seed-db
```

### Problem: Template not found
```bash
# Check if templates directory exists
ls templates/

# Should contain:
# base.html
# faculty_list.html
# faculty_form.html
# faculty_view.html
```

### Problem: 500 Internal Server Error
```bash
# Run in debug mode to see error
export FLASK_DEBUG=1  # Linux/Mac
set FLASK_DEBUG=1     # Windows
python app.py
```

## 📊 Database Schema

### Tables
- **department**: id, name
- **subject**: id, subject_code, subject_name
- **faculty**: id, name, email, phone, department_id, designation, qualification, experience_years, created_at
- **faculty_subject**: id, faculty_id, subject_id, semester
- **faculty_attendance**: id, faculty_id, date, status, remarks
- **faculty_leave**: id, faculty_id, leave_type, from_date, to_date, reason, status, applied_on

### Relationships
```
Department (1) ←→ (Many) Faculty
Faculty (Many) ←→ (Many) Subject (through faculty_subject)
Faculty (1) ←→ (Many) FacultyAttendance
Faculty (1) ←→ (Many) FacultyLeave
```

## 🎯 Application Features

### Faculty Management
- ✅ Add new faculty
- ✅ Edit existing faculty
- ✅ Delete faculty
- ✅ View faculty details
- ✅ List all faculty

### Subject Assignment
- ✅ Assign multiple subjects
- ✅ Track by semester
- ✅ Prevent duplicate assignments

### Validation
- ✅ Email uniqueness
- ✅ Phone format (10 digits)
- ✅ Required fields
- ✅ CSRF protection

## 🌐 URLs

### Main Routes
```
GET  /                      → Redirect to faculty list
GET  /faculty/list          → List all faculty
GET  /faculty/add           → Show add faculty form
POST /faculty/add           → Create new faculty
GET  /faculty/edit/<id>     → Show edit faculty form
POST /faculty/edit/<id>     → Update faculty
GET  /faculty/view/<id>     → View faculty details
POST /faculty/delete/<id>   → Delete faculty
```

## 📝 Sample Data (After seed-db)

### Departments
- Computer Science
- Electronics
- Mechanical
- Civil
- Mathematics

### Subjects
- CS101 - Data Structures
- CS102 - Database Management
- CS103 - Operating Systems
- EC101 - Digital Electronics
- ME101 - Thermodynamics
- MA101 - Linear Algebra

## 🔐 Security Features

- ✅ CSRF protection (enabled)
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ XSS prevention (Jinja2 auto-escaping)
- ✅ Unique email constraint
- ✅ Form validation

## 📦 Dependencies

```
Flask==2.3.2              # Web framework
Flask-SQLAlchemy==3.1.1   # Database ORM
Flask-WTF==1.2.1          # Forms
Bootstrap-Flask==2.2.0    # UI components
WTForms==3.0.1            # Form validation
SQLAlchemy==2.0.25        # Database toolkit
Werkzeug==3.0.0           # WSGI utilities
```

## 💡 Tips

1. **Always use virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. **Backup database before major changes:**
   ```bash
   cp college.db college.db.backup
   ```

3. **Check logs for errors:**
   - Console output shows all errors in debug mode
   - Look for stack traces

4. **Use debug mode in development:**
   ```python
   # In app.py (already enabled)
   if __name__ == '__main__':
       app.run(debug=True)
   ```

5. **Test changes incrementally:**
   - Make small changes
   - Test after each change
   - Commit working code

## 🆘 Getting Help

### Check These First:
1. README.md - Complete setup guide
2. ERROR_ANALYSIS.md - Detailed error explanations
3. verify.py - Run automated tests
4. Console output - Read error messages

### Common Error Messages:

**"TemplateNotFound"**
→ Templates directory missing or wrong name

**"No module named 'flask_bootstrap'"**
→ Run: `pip install Bootstrap-Flask`

**"IntegrityError: UNIQUE constraint"**
→ Email or subject assignment already exists

**"Working outside of application context"**
→ Wrap database operations in `with app.app_context():`

## 📞 Support Checklist

Before asking for help, verify:
- [ ] All files present (check with verify.py)
- [ ] Dependencies installed
- [ ] Database initialized
- [ ] No syntax errors
- [ ] Correct Python version (3.8+)
- [ ] Virtual environment activated
- [ ] Read error message completely

---

**Quick Start:** `./setup.sh && python app.py`
**Documentation:** See README.md
**Status Check:** `python verify.py`
