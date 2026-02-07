import click
from flask.cli import with_appcontext
from models import db, Admin, Department, Subject, Classroom, AcademicClass
from werkzeug.security import generate_password_hash

@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    db.create_all()
    click.echo("Initialized the database.")

@click.command("seed-db")
@with_appcontext
def seed_db_command():
    """Seed the database with initial data."""
    # check if data exists
    if Department.query.first():
        click.echo("Database already seeded.")
        return

    # Add Departments
    dept_cse = Department(name="Computer Science")
    dept_ece = Department(name="Electronics")
    dept_mech = Department(name="Mechanical")
    
    db.session.add_all([dept_cse, dept_ece, dept_mech])
    db.session.commit()
    
    click.echo("Seeded Departments.")

    # Add Subjects
    sub_python = Subject(subject_code="CS101", subject_name="Python Programming")
    sub_dbms = Subject(subject_code="CS102", subject_name="Database Management")
    
    db.session.add_all([sub_python, sub_dbms])
    db.session.commit()
    
    click.echo("Seeded Subjects.")
    
    # Add Classrooms
    room_101 = Classroom(room_code="101", room_type="Lecture", capacity=60)
    room_102 = Classroom(room_code="102", room_type="Lab", capacity=30)
    
    db.session.add_all([room_101, room_102])
    db.session.commit()

    click.echo("Seeded Classrooms.")
    click.echo("Database seeded successfully.")

@click.command("create-admin")
@click.option("--username", prompt="USERNAME", help="Admin username")
@click.option("--password", prompt="PASSWORD", hide_input=True, confirmation_prompt=True, help="Admin password")
@with_appcontext
def create_admin_command(username, password):
    """Create a new admin user."""
    if Admin.query.filter_by(username=username).first():
        click.echo(f"Error: Admin '{username}' already exists.")
        return
    
    admin = Admin(username=username)
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    click.echo(f"Success! Admin '{username}' created.")

def register_commands(app):
    """Register CLI commands with the application."""
    app.cli.add_command(init_db_command)
    app.cli.add_command(seed_db_command)
    app.cli.add_command(create_admin_command)
