from flask import Blueprint, render_template, session
from src.utils.decorators import login_required
from src.models.user import User
from src.models.course import Course, users_courses
from src.extensions import db

account_bp = Blueprint('account', __name__)

@account_bp.route("/account")
@login_required
def account():
    """Show user account profile"""
    session["cart"] = []
    
    user = User.query.get(session["user_id"])
    
    # Get courses the user is enrolled in using the association table
    enrolled_courses = db.session.query(Course).join(users_courses).filter(users_courses.c.user_id == user.id).all()

    # See if user has enroled in any course
    if not enrolled_courses:
        return render_template("pages/account/profile.html")

    return render_template("pages/account/profile.html", ids=enrolled_courses)

@account_bp.route("/remove_course", methods=["POST"])
@login_required
def remove_course():
    from flask import request, redirect, url_for, flash
    course_id = request.form.get("course_id")
    user_id = session.get("user_id")
    
    if user_id and course_id:
        db.session.execute(users_courses.delete().where(
            (users_courses.c.user_id == user_id) & 
            (users_courses.c.course_id == int(course_id))
        ))
        db.session.commit()
        flash("კურსი ამოშლილია სილაბუსიდან", "success")
    
    return redirect(url_for("account.account"))
