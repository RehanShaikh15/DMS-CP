#!/usr/bin/env python3
"""
Faculty Management System - Verification Test Script
This script tests if all components are working correctly
"""

import sys
import os

def print_status(test_name, passed, message=""):
    """Print test status with colored output"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test_name}")
    if message:
        print(f"    → {message}")

def test_imports():
    """Test if all required modules can be imported"""
    print("\n🔍 Testing Imports...")
    
    tests = {
        "Flask": "flask",
        "SQLAlchemy": "flask_sqlalchemy",
        "WTForms": "wtforms",
        "Bootstrap-Flask": "flask_bootstrap"
    }
    
    all_passed = True
    for name, module in tests.items():
        try:
            __import__(module)
            print_status(name, True)
        except ImportError as e:
            print_status(name, False, str(e))
            all_passed = False
    
    return all_passed

def test_file_structure():
    """Test if required files exist"""
    print("\n📁 Testing File Structure...")
    
    required_files = [
        "app.py",
        "models.py",
        "forms.py",
        "config.py",
        "requirements.txt"
    ]
    
    required_dirs = [
        "templates",
        "static"
    ]
    
    required_templates = [
        "templates/base.html",
        "templates/faculty_list.html",
        "templates/faculty_form.html",
        "templates/faculty_view.html"
    ]
    
    all_passed = True
    
    for file in required_files:
        exists = os.path.exists(file)
        print_status(f"File: {file}", exists)
        if not exists:
            all_passed = False
    
    for directory in required_dirs:
        exists = os.path.isdir(directory)
        print_status(f"Directory: {directory}", exists)
        if not exists:
            all_passed = False
    
    for template in required_templates:
        exists = os.path.exists(template)
        print_status(f"Template: {template}", exists)
        if not exists:
            all_passed = False
    
    return all_passed

def test_app_creation():
    """Test if Flask app can be created"""
    print("\n🚀 Testing App Creation...")
    
    try:
        from app import app, db
        print_status("Flask app creation", True)
        
        # Test app configuration
        has_secret = bool(app.config.get('SECRET_KEY'))
        print_status("SECRET_KEY configured", has_secret)
        
        has_db_uri = bool(app.config.get('SQLALCHEMY_DATABASE_URI'))
        print_status("Database URI configured", has_db_uri)
        
        return True
    except Exception as e:
        print_status("Flask app creation", False, str(e))
        return False

def test_models():
    """Test if database models can be imported"""
    print("\n📊 Testing Database Models...")
    
    try:
        from models import Faculty, Department, Subject, FacultySubject
        print_status("Model imports", True)
        
        # Check if models have required attributes
        has_faculty_attrs = hasattr(Faculty, 'name') and hasattr(Faculty, 'email')
        print_status("Faculty model attributes", has_faculty_attrs)
        
        has_dept_attrs = hasattr(Department, 'name')
        print_status("Department model attributes", has_dept_attrs)
        
        has_subject_attrs = hasattr(Subject, 'subject_code')
        print_status("Subject model attributes", has_subject_attrs)
        
        return True
    except Exception as e:
        print_status("Model imports", False, str(e))
        return False

def test_forms():
    """Test if forms can be imported"""
    print("\n📝 Testing Forms...")
    
    try:
        from forms import FacultyForm
        print_status("Form imports", True)
        
        # Check if form has required fields
        form = FacultyForm()
        has_name = hasattr(form, 'name')
        has_email = hasattr(form, 'email')
        has_department = hasattr(form, 'department')
        
        print_status("Form has name field", has_name)
        print_status("Form has email field", has_email)
        print_status("Form has department field", has_department)
        
        return True
    except Exception as e:
        print_status("Form imports", False, str(e))
        return False

def test_database_init():
    """Test if database can be initialized"""
    print("\n🗄️  Testing Database Initialization...")
    
    try:
        from app import app, db
        
        with app.app_context():
            # Try to create tables
            db.create_all()
            print_status("Database tables created", True)
            
            # Check if database file exists
            db_exists = os.path.exists('college.db')
            print_status("Database file exists", db_exists)
            
            return True
    except Exception as e:
        print_status("Database initialization", False, str(e))
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Faculty Management System - Verification Tests")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("File Structure", test_file_structure()))
    results.append(("App Creation", test_app_creation()))
    results.append(("Models", test_models()))
    results.append(("Forms", test_forms()))
    results.append(("Database", test_database_init()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 All tests passed! Your application is ready to run.")
        print("\nTo start the application:")
        print("  python app.py")
        print("\nOr:")
        print("  flask --app app run --debug")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Make sure all files are in the correct directory")
        print("  3. Check for syntax errors in Python files")
        return 1

if __name__ == "__main__":
    sys.exit(main())
