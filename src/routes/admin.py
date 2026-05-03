import os
from flask import Blueprint, render_template, request, session, redirect, flash, current_app
from werkzeug.utils import secure_filename
from src.utils.decorators import admin_required
from src.models.user import User
from src.models.course import Course, Promo, users_courses
from src.extensions import db

admin_bp = Blueprint('admin', __name__)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_bp.route("/admin")
@admin_required
def admin():
    """Admin dashboard"""
    stats = {
        "users": User.query.filter_by(admin=0).count(),
        "courses": Course.query.count(),
        "revenue": 0 # Placeholder logic could be added here
    }
    return render_template("pages/admin/dashboard.html", stats=stats)

@admin_bp.route("/admin/courses")
@admin_required
def admin_courses():
    courses = Course.query.all()
    return render_template("pages/admin/courses.html", courses=courses)

@admin_bp.route("/admin/users")
@admin_required
def admin_users():
    users = User.query.all()
    return render_template("pages/admin/users.html", users=users)

@admin_bp.route("/admin/stats")
@admin_required
def admin_stats():
    stats = {
        "total_users": User.query.count(),
        "total_courses": Course.query.count()
    }
    return render_template("pages/admin/stats.html", stats=stats)

@admin_bp.route("/admin/courses/new", methods=["GET", "POST"])
@admin_required
def add_course():
    if request.method == "POST":
        title = request.form.get("name")
        description = request.form.get("description")
        price = float(request.form.get("price", 0))
        
        file = request.files.get("image")
        image_filename = "default_course.jpg"
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config["COURSE_UPLOAD_FOLDER"], filename))
            image_filename = filename
            
        new_course = Course(name=title, description=description, price=price, image=image_filename)
        db.session.add(new_course)
        db.session.commit()
        
        flash("კურსი წარმატებით დაემატა!")
        return redirect("/admin/courses")
        
    return render_template("pages/admin/add_course.html")

@admin_bp.route("/admin/courses/edit/<int:course_id>", methods=["GET", "POST"])
@admin_required
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
        
    if request.method == "POST":
        course.name = request.form.get("name")
        course.description = request.form.get("description")
        course.price = float(request.form.get("price", 0))
        
        file = request.files.get("image")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config["COURSE_UPLOAD_FOLDER"], filename))
            course.image = filename
            
        db.session.commit()
        flash("კურსი განახლდა!")
        return redirect("/admin/courses")
        
    return render_template("pages/admin/edit_course.html", course=course)

@admin_bp.route("/admin/courses/delete/<int:course_id>")
@admin_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    # SQLAlchemy handles deletion from association table if configured, 
    # but we'll do it manually here for safety based on current schema
    db.session.execute(users_courses.delete().where(users_courses.c.course_id == course_id))
    db.session.delete(course)
    db.session.commit()
    flash("კურსი წაიშალა!")
    return redirect("/admin/courses")

@admin_bp.route("/admin/users/delete/<int:user_id>")
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.username == "admin":
        flash("ადმინისტრატორის წაშლა შეუძლებელია!")
    else:
        db.session.execute(users_courses.delete().where(users_courses.c.user_id == user_id))
        db.session.delete(user)
        db.session.commit()
        flash("მომხმარებელი წაიშალა!")
    return redirect("/admin/users")

@admin_bp.route("/admin/cupon", methods=["GET", "POST"])
@admin_required
def admin_cupon():
    if request.method == "POST":
        name = request.form.get("name")
        value = int(request.form.get("value", 0))
        promo_id = request.form.get("promo_id")

        if not promo_id:
            new_promo = Promo(name=name.upper(), value=value)
            db.session.add(new_promo)
            flash(f"კუპონი '{name}' დაემატა!")
        else:
            promo = Promo.query.get(promo_id)
            if promo:
                promo.name = name.upper()
                promo.value = value
                flash(f"კუპონი '{name}' განახლდა!")
        
        db.session.commit()
        return redirect("/admin/cupon")
    
    coupons = Promo.query.all()
    return render_template("pages/admin/coupons.html", cupon=coupons)
