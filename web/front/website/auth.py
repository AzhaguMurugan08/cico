from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from .models import User, StudentCheckInOut, Student, db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
from pytz import timezone
from itertools import groupby
import sys
from settings.config import passkey

auth = Blueprint("auth", __name__)

def convert_to_local_time(utc_dt, local_tz='Asia/Kolkata'):
    return utc_dt.replace(tzinfo=timezone('UTC')).astimezone(timezone(local_tz))

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        mode = request.form.get("mode")

        if mode == "signup":
            email = request.form.get("email")
            name = request.form.get("name")
            role = request.form.get("role")
            phone = request.form.get("phone")
            age = request.form.get("age")
            address = request.form.get("address")
            password1 = request.form.get("password1")
            password2 = request.form.get("password2")
            batch_number = request.form.get("batch_number")
           

            # Check if the user already exists
            if User.query.filter_by(email=email).first():
                flash("User already exists", 'error')
                return render_template("login.html", user=current_user)

            # Check if passwords match
            if password1 != password2:
                flash("Passwords do not match!", 'error')
                return render_template("login.html", user=current_user)

            # Ensure password is strong enough
            if len(password1) < 6:
                flash("Password must be at least 6 characters long.", 'error')
                return render_template("login.html", user=current_user)

            # Check for age and address if the role is "user" (Watchman)
            if role == "user":
                if not age or not age.isdigit() or int(age) <= 0:
                    flash("Please provide a valid age.", 'error')
                    return render_template("login.html", user=current_user)
                if not address:
                    flash("Please provide an address.", 'error')
                    return render_template("login.html", user=current_user)
                
           

            # Create new user
            new_user = User(
                email=email,
                name=name,
                role=role,
                phone=phone,
                age=int(age) if role == "user" else None,
                address=address if role == "user" else None,
                password=generate_password_hash(password1, method="sha256"),
                batch_number=batch_number if role == "user" else None,
                is_approved=True if role == "staff" else False
            )
            db.session.add(new_user)
            db.session.commit()

            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for("auth.login"))

        else:
            # Login logic
            email = request.form.get("email")
            password = request.form.get("password")
            batch_number = request.form.get("batch_number")
            entered_passkey = request.form.get("passkey")

            # Check if email or password is empty
            if not email or not password:
                flash("Please provide both email and password.", 'error')
                return render_template("login.html", user=current_user)

            # Get the user from the database
            user = User.query.filter_by(email=email).first()

            # Validate user and password
            if not user or not check_password_hash(user.password, password):
                flash("Invalid email or password.", 'error')
                return render_template("login.html", user=current_user)
            
             # Check passkey for staff role
            if user.role == "staff":
                if not entered_passkey:
                    flash("Passkey is required for admin login.", 'error')
                    return render_template("login.html", user=current_user)
                   
                if user.passkey != entered_passkey:
                    flash("Invalid passkey.", 'error')
                    return render_template("login.html", user=current_user)

            # Logic for watchman role
            if user.role == "user":
                if not batch_number:
                    flash("Batch number is required for Watchmen.", 'error')
                    return render_template("login.html", user=current_user)
                if user.batch_number != batch_number:
                    flash("Invalid batch number.", 'error')
                    return render_template("login.html", user=current_user)
                if not user.is_approved:
                    flash("Your account is not approved yet.", 'info')
                    return render_template("login.html", user=current_user)

                session["batch_number"] = batch_number

            login_user(user, remember=True)

            # Redirect based on role
            if user.role == "staff":
                return redirect(url_for("auth.admin_dashboard"))
            else:
                return redirect(url_for("auth.home"))

    return render_template("login.html", user=current_user)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    session.pop("batch_number", None)
    return redirect(url_for("auth.login"))

@auth.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "staff":
        return redirect(url_for("auth.login"))

    # Query for pending admins
    watchmen = User.query.filter_by(role="user", is_approved=True).all()
    pending_admins = User.query.filter_by(role="staff", is_approved=False).all()
    pending_users = User.query.filter_by(role="user", is_approved=False).all()

    total_users = User.query.count()

    # Query for logged-in admins
    logged_in_admins = User.query.filter_by(role="staff", is_approved=True).all()

    # Query for check-in and check-out records
    checkin_records = StudentCheckInOut.query.filter_by(status="in").order_by(StudentCheckInOut.timestamp.desc()).all()
    checkout_records = StudentCheckInOut.query.filter_by(status="out").order_by(StudentCheckInOut.timestamp.desc()).all()

    since = datetime.utcnow() - timedelta(hours=24)

    checkin_count = StudentCheckInOut.query.filter(
        StudentCheckInOut.status == "in",
        StudentCheckInOut.timestamp >= since
    ).count()

    checkout_count = StudentCheckInOut.query.filter(
        StudentCheckInOut.status == "out",
        StudentCheckInOut.timestamp >= since
    ).count()

    # Group records by date
    grouped_checkin_records = {
        date: list(records) for date, records in groupby(
            checkin_records, key=lambda x: x.timestamp.date()
        )
    }
    grouped_checkout_records = {
        date: list(records) for date, records in groupby(
            checkout_records, key=lambda x: x.timestamp.date()
        )
    }

    return render_template(
        "admin_dashboard.html",
        admin=current_user,
        checkin_count=checkin_count,
        checkout_count=checkout_count,
        total_watchmen=len(watchmen),
        pending_users=pending_users,
        pending_admins=pending_admins,
        watchmen=watchmen,
        grouped_checkin_records=grouped_checkin_records,
        grouped_checkout_records=grouped_checkout_records,
        total_users=total_users,
        logged_in_admins=logged_in_admins  # Pass logged-in admins to the template
    )

@auth.route("/approve/<int:user_id>", methods=["POST"])
@login_required
def approve_watchman(user_id):
    if current_user.role != "staff":
        flash("You are not authorized to approve watchmen.", "error")
        return redirect(url_for("auth.admin_dashboard"))

    # Get the passkey from the form
    passkey = request.form.get("passkey")
    from settings.config import passkey  # Import the common passkey

    # Validate the passkey
    if passkey !=  passkey :
        flash("Invalid passkey. Approval denied.", "error")
        return redirect(url_for("auth.admin_dashboard"))

    # Fetch the watchman to be approved
    user = User.query.get(user_id)
    if user and user.role == "user":
        user.is_approved = True
        db.session.commit()
        flash(f"Watchman {user.name} approved successfully.", "success")
    else:
        flash("Invalid watchman or user not found.", "error")

    return redirect(url_for("auth.admin_dashboard"))

@auth.route("/deny/<int:user_id>", methods=["POST"])
@login_required
def deny_watchman(user_id):
    if current_user.role != "staff":
        return redirect(url_for("auth.admin_dashboard"))

    user = User.query.get(user_id)
    if user and user.role == "user":
        db.session.delete(user)  # Remove the user from the database
        db.session.commit()

    flash(f"Watchman {user.name} has been removed from the list.", 'danger')
    return redirect(url_for("auth.admin_dashboard"))

@auth.route("/approve_admin/<int:user_id>", methods=["POST"])
@login_required
def approve_admin(user_id):
    # Ensure only staff can approve admins
    if current_user.role != "staff":
        flash("You are not authorized to approve admins.", "error")
        return redirect(url_for("auth.admin_dashboard"))

    # Get the passkey from the form
    entered_passkey = request.form.get("passkey")

    # Validate the passkey against the current admin's passkey
    if current_user.passkey != entered_passkey:
        flash("Invalid passkey. Approval denied.", "error")
        return redirect(url_for("auth.admin_dashboard"))

    # Fetch the admin to be approved
    user = User.query.get(user_id)
    if user and user.role == "staff" and not user.is_approved:
        user.is_approved = True
        db.session.commit()
        flash(f"Admin {user.name} approved successfully.", "success")
    else:
        flash("Invalid admin or user not found.", "error")

    return redirect(url_for("auth.admin_dashboard"))

@auth.route("/student_check_in", methods=["GET", "POST"])
@login_required
def student_check_in():
    if current_user.role != "user":
        return redirect(url_for("auth.home"))

    if request.method == "POST":
        name = request.form.get("name")
        roll_number = request.form.get("roll_number")
        department = request.form.get("department")
        year = request.form.get("year")  

        if not all([name, roll_number, department, year]):  
            flash("Please provide all required fields.", 'error')
            return redirect(url_for("auth.student_check_in"))

        entry = StudentCheckInOut(
            student_name=name,
            roll_number=roll_number,
            department=department,
            year=year,  
            status="in",
            timestamp=datetime.utcnow(),
            watchman_id=current_user.id
        )
        db.session.add(entry)
        db.session.commit()

        flash('Student checked in successfully.', 'success')
        return redirect(url_for("auth.home"))

    return render_template("check_in.html", user=current_user)

@auth.route("/student_check_out", methods=["GET", "POST"])
@login_required
def student_check_out():
    if current_user.role != "user":
        return redirect(url_for("auth.home"))

    if request.method == "POST":
        name = request.form.get("name")
        roll_number = request.form.get("roll_number")
        department = request.form.get("department")
        year = request.form.get("year") 

        if not all([name, roll_number, department, year]):  # Include year in validation
            flash("Please provide all required fields.", 'error')
            return redirect(url_for("auth.student_check_out"))

        entry = StudentCheckInOut(
            student_name=name,
            roll_number=roll_number,
            department=department,
            year=year,  # Save year to the database
            status="out",
            timestamp=datetime.utcnow(),
            watchman_id=current_user.id
        )
        db.session.add(entry)
        db.session.commit()

        flash('Student checked out successfully.', 'success')
        return redirect(url_for("auth.home"))

    return render_template("check_out.html", user=current_user)

@auth.route("/")
@login_required
def home():
    if current_user.role != "user":
        return redirect(url_for("auth.admin_dashboard"))

    last_24_hours = datetime.utcnow() - timedelta(hours=24)

    checkin_logs = StudentCheckInOut.query.filter(
        StudentCheckInOut.status == "in",
        StudentCheckInOut.timestamp >= last_24_hours
    ).order_by(StudentCheckInOut.timestamp.desc()).all()

    checkout_logs = StudentCheckInOut.query.filter(
        StudentCheckInOut.status == "out",
        StudentCheckInOut.timestamp >= last_24_hours
    ).order_by(StudentCheckInOut.timestamp.desc()).all()

    for log in checkin_logs:
        log.timestamp = convert_to_local_time(log.timestamp)
    for log in checkout_logs:
        log.timestamp = convert_to_local_time(log.timestamp)

    return render_template(
        "home.html",
        user=current_user,
        checkin_logs=checkin_logs,
        checkout_logs=checkout_logs,
        checkin_count=len(checkin_logs),
        checkout_count=len(checkout_logs)
    )

@auth.route("/get_student_details", methods=["POST"])
@login_required
def get_student_details():
    data = request.get_json()
    roll_number = data.get("roll_number")

    student = Student.query.filter_by(roll_number=roll_number).first()

    if student:
        return jsonify({
            "name": student.name,
            "department": student.department,
            "year": student.year
        })
    else:
        return jsonify({"error": "Student not found"}), 404
