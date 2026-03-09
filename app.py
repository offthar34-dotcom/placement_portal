from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///placement.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# DATABASE MODELS


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))
    course = db.Column(db.String(50))
    branch = db.Column(db.String(50))
    cgpa = db.Column(db.Float)


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100))
    hr_email = db.Column(db.String(100))
    password = db.Column(db.String(100))
    website = db.Column(db.String(200))
    status = db.Column(db.String(50), default="Pending")


class Drive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer)
    job_title = db.Column(db.String(100))
    description = db.Column(db.Text)
    eligibility = db.Column(db.String(100))
    deadline = db.Column(db.String(50))
    status = db.Column(db.String(50), default="Pending")


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer)
    drive_id = db.Column(db.Integer)
    date = db.Column(db.String(50))
    status = db.Column(db.String(50), default="Applied")


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))


# CREATE DATABASE


@app.before_request
def create_tables():
    db.create_all()

    if Admin.query.first() is None:
        admin = Admin(username="admin", password="admin")
        db.session.add(admin)
        db.session.commit()


# LOGIN


@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        role = request.form["role"]
        email = request.form["email"]
        password = request.form["password"]

        if role == "student":
            user = Student.query.filter_by(email=email, password=password).first()
            if user:
                session["student"] = user.id
                return redirect("/student_dashboard")

        if role == "company":
            user = Company.query.filter_by(hr_email=email, password=password, status="Approved").first()
            if user:
                session["company"] = user.id
                return redirect("/company_dashboard")

        if role == "admin":
            user = Admin.query.filter_by(username=email, password=password).first()
            if user:
                session["admin"] = user.id
                return redirect("/admin_dashboard")

    return render_template("login.html")


# STUDENT REGISTRATION

@app.route("/register_student", methods=["GET","POST"])
def register_student():

    if request.method == "POST":

        student = Student(
            name=request.form["name"],
            email=request.form["email"],
            password=request.form["password"],
            course=request.form["course"],
            branch=request.form["branch"],
            cgpa=request.form["cgpa"]
        )

        db.session.add(student)
        db.session.commit()

        return redirect("/")

    return render_template("register_student.html")


# COMPANY REGISTRATION


@app.route("/register_company", methods=["GET","POST"])
def register_company():

    if request.method == "POST":

        company = Company(
            company_name=request.form["company_name"],
            hr_email=request.form["email"],
            password=request.form["password"],
            website=request.form["website"]
        )

        db.session.add(company)
        db.session.commit()

        return redirect("/")

    return render_template("register_company.html")


# STUDENT DASHBOARD


@app.route("/student_dashboard")
def student_dashboard():

    drives = Drive.query.filter_by(status="Approved").all()

    return render_template("student_dashboard.html", drives=drives)


# APPLY DRIVE


@app.route("/apply/<int:drive_id>")
def apply(drive_id):

    student_id = session.get("student")

    existing = Application.query.filter_by(
        student_id=student_id,
        drive_id=drive_id
    ).first()

    if existing:
        return "Already applied"

    application = Application(
        student_id=student_id,
        drive_id=drive_id,
        date=str(datetime.now())
    )

    db.session.add(application)
    db.session.commit()

    return redirect("/student_dashboard")


# COMPANY DASHBOARD

@app.route("/company_dashboard")
def company_dashboard():

    company_id = session.get("company")

    drives = Drive.query.filter_by(company_id=company_id).all()

    return render_template("company_dashboard.html", drives=drives)


# CREATE DRIVE

@app.route("/create_drive", methods=["GET","POST"])
def create_drive():

    if request.method == "POST":

        drive = Drive(
            company_id=session["company"],
            job_title=request.form["title"],
            description=request.form["description"],
            eligibility=request.form["eligibility"],
            deadline=request.form["deadline"]
        )

        db.session.add(drive)
        db.session.commit()

        return redirect("/company_dashboard")

    return render_template("create_drive.html")
  
# ADMIN DASHBOARD

@app.route("/admin_dashboard")
def admin_dashboard():

    students = Student.query.count()
    companies = Company.query.count()
    drives = Drive.query.count()
    applications = Application.query.count()

    return render_template(
        "admin_dashboard.html",
        students=students,
        companies=companies,
        drives=drives,
        applications=applications
    )
# APPROVE COMPANY

@app.route("/approve_company/<int:id>")
def approve_company(id):

    company = Company.query.get(id)
    company.status = "Approved"

    db.session.commit()

    return redirect("/admin_dashboard")

if __name__ == "__main__":
    app.run(debug=True)
