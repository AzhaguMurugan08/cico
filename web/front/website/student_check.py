from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import StudentCheckInOut, db
from datetime import datetime

student_check = Blueprint("student_check", __name__)

@student_check.route("/check_in", methods=["GET", "POST"])
@login_required
def check_in():
    if request.method == "POST":
        student_name = request.form.get("student_name")
        roll_number = request.form.get("roll_number")
        department = request.form.get("department")

        new_checkin = StudentCheckInOut(
            student_name=student_name,
            roll_number=roll_number,
            department=department,
            status='in',
            timestamp=datetime.now(),
            watchman_id=current_user.id
        )

        db.session.add(new_checkin)
        db.session.commit()
        flash("Student checked in successfully!", category="success")
        return redirect(url_for("views.home"))

    return render_template("check_in.html", user=current_user)

@student_check.route("/check_out", methods=["GET", "POST"])
@login_required
def check_out():
    if request.method == "POST":
        student_name = request.form.get("student_name")
        roll_number = request.form.get("roll_number")
        department = request.form.get("department")
        reason = request.form.get("reason")

        new_checkout = StudentCheckInOut(
            student_name=student_name,
            roll_number=roll_number,
            department=department,
            reason=reason,
            status='out',
            timestamp=datetime.now(),
            watchman_id=current_user.id
        )

        db.session.add(new_checkout)
        db.session.commit()
        flash("Student checked out successfully!", category="success")
        return redirect(url_for("views.home"))

    return render_template("check_out.html", user=current_user)
