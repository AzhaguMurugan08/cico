from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .models import StudentCheckInOut
from datetime import datetime, timedelta

views = Blueprint("views", __name__)

@views.route("/")
@login_required
def home():
    # Only allow watchmen (user role) to view this dashboard
    if current_user.role != "user":
        return render_template("unauthorized.html", user=current_user)

    # Get student check-in and check-out logs from the last 24 hours
    last_24_hours = datetime.now() - timedelta(hours=24)

    checkin_logs = StudentCheckInOut.query.filter(
        StudentCheckInOut.status == "in",
        StudentCheckInOut.timestamp >= last_24_hours
    ).order_by(StudentCheckInOut.timestamp.desc()).all()

    checkout_logs = StudentCheckInOut.query.filter(
        StudentCheckInOut.status == "out",
        StudentCheckInOut.timestamp >= last_24_hours
    ).order_by(StudentCheckInOut.timestamp.desc()).all()

    return render_template(
        "home.html",
        user=current_user,
        checkin_logs=checkin_logs,
        checkout_logs=checkout_logs,
        checkin_count=len(checkin_logs),
        checkout_count=len(checkout_logs)
    )
