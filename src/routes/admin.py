import os
from sqlalchemy import func
from flask import Blueprint, render_template, request, session, redirect, flash, current_app
from datetime import datetime, date
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
    user_count = User.query.filter_by(admin=0).count()
    course_count = Course.query.count()
    enrollment_count = db.session.query(users_courses).count()
    
    # Fetch recent activity (e.g., last 5 enrollments)
    recent_activity = db.session.query(
        User.username, 
        Course.name.label('course_name'),
        # Since users_courses is an association table, we join User and Course
    ).join(users_courses, User.id == users_courses.c.user_id) \
     .join(Course, Course.id == users_courses.c.course_id) \
     .order_by(db.desc(users_courses.c.user_id)) \
     .limit(5).all()
    
    return render_template("pages/admin/dashboard.html", 
                           user_count=user_count, 
                           course_count=course_count, 
                           enrollment_count=enrollment_count,
                           recent_activity=recent_activity)

@admin_bp.route("/admin/courses")
@admin_required
def admin_courses():
    page = request.args.get('page', 1, type=int)
    courses_pagination = Course.query.order_by(Course.id.desc()).paginate(page=page, per_page=10, error_out=False)
    return render_template("pages/admin/courses.html", courses=courses_pagination.items, pagination=courses_pagination)

@admin_bp.route("/admin/users")
@admin_required
def admin_users():
    page = request.args.get('page', 1, type=int)
    users_pagination = User.query.order_by(User.id.desc()).paginate(page=page, per_page=10, error_out=False)
    return render_template("pages/admin/users.html", users=users_pagination.items, pagination=users_pagination)

@admin_bp.route("/admin/stats")
@admin_required
def admin_stats():
    total_users = User.query.count()
    total_courses = Course.query.count()
    total_enrollments = db.session.query(users_courses).count()
    
    recent_users = User.query.order_by(User.id.desc()).limit(5).all()
    
    popular_courses_raw = db.session.query(
        Course.name, 
        func.count(users_courses.c.user_id).label('enrollments')
    ).join(users_courses, Course.id == users_courses.c.course_id) \
     .group_by(Course.id) \
     .order_by(func.count(users_courses.c.user_id).desc()) \
     .limit(5).all()
    
    stats = {
        "total_users": total_users,
        "total_courses": total_courses,
        "total_enrollments": total_enrollments,
        "recent_users": recent_users,
        "popular_courses": popular_courses_raw
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

@admin_bp.route("/admin/coupons")
@admin_bp.route("/admin/cupon", methods=["GET", "POST"])
@admin_required
def admin_cupon():
    if request.method == "POST":
        name = request.form.get("name")
        try:
            value = int(request.form.get("value", 0))
        except ValueError:
            value = 0
            
        promo_id = request.form.get("id") or request.form.get("promo_id")
        expiry_str = request.form.get("expiry_date")
        
        expiry_date = None
        if expiry_str:
            try:
                expiry_date = datetime.strptime(expiry_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        if request.form.get("delete"):
            promo = Promo.query.get(promo_id)
            if promo:
                db.session.delete(promo)
                db.session.commit()
                flash(f"კუპონი წაიშალა")
            return redirect("/admin/cupon")

        if not promo_id:
            new_promo = Promo(name=name.upper(), value=value, expiry_date=expiry_date)
            db.session.add(new_promo)
            flash(f"კუპონი '{name}' დაემატა!")
        else:
            promo = Promo.query.get(promo_id)
            if promo:
                promo.name = name.upper()
                promo.value = value
                promo.expiry_date = expiry_date
                flash(f"კუპონი '{name}' განახლდა!")
        
        db.session.commit()
        return redirect("/admin/cupon")
    
    # Sort coupons: Active first, then expired
    coupons = Promo.query.all()
    today_date = date.today()
    
    # Custom sort: 0 for active, 1 for expired
    def sort_key(p):
        is_expired = p.expiry_date and p.expiry_date < today_date
        return (1 if is_expired else 0, p.name)
    
    sorted_coupons = sorted(coupons, key=sort_key)
    
    return render_template("pages/admin/coupons.html", cupon=sorted_coupons, today=today_date)
