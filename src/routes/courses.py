from flask import Blueprint, render_template, request, session, redirect, flash
from src.utils.decorators import register_required
from src.models.course import Course, Promo, users_courses
from src.models.user import User
from src.extensions import db

courses_bp = Blueprint('courses', __name__)

@courses_bp.route("/courses")
def courses():
    """List all Courses"""
    session["cart"] = []

    try:
        courses = Course.query.all()
        enrolled_course_ids = []
        
        if session.get("user_id"):
            # Get IDs of courses the user is enrolled in
            enrollments = db.session.query(users_courses.c.course_id).filter(users_courses.c.user_id == session["user_id"]).all()
            enrolled_course_ids = [e.course_id for e in enrollments]

        # Add enrollment status to each course object for the template
        for course in courses:
            course.is_enrolled = course.id in enrolled_course_ids

        return render_template("pages/courses/list.html", ids=courses)
    except Exception as e:
        print(f"Error loading courses: {e}")
        return render_template("pages/courses/list.html", ids=[])

@courses_bp.route("/info")
def info():
    """Show specific course information"""
    course_id = request.args.get("id")
    if not course_id:
        return redirect("/courses")
    
    course = Course.query.get_or_404(course_id)
    
    # Check if user is enrolled
    is_enrolled = False
    if session.get("user_id"):
        is_enrolled = db.session.query(users_courses).filter_by(
            user_id=session["user_id"], 
            course_id=course.id
        ).first() is not None
        
    return render_template("pages/courses/details.html", course=course, is_enrolled=is_enrolled)

@courses_bp.route("/buy", methods=["GET", "POST"])
@register_required
def buy():
    """Purchase courses"""
    if session.get("admin"):
        flash("ადმინებს არ შეუძლიათ კურსების შეძენა")
        return redirect("/admin")

    if "cart" not in session:
        session["cart"] = []

    if "promo" not in session:
        session["promo"] = []

    # POST
    if request.method == "POST":
        course_id = request.form.get("id")
        payment_email = request.form.get("email")
        promo_name = request.form.get("promo")

        # If adding a course to cart or buying free course
        if course_id:
            course_id = int(course_id)
            course = Course.query.get(course_id)
            
            # Check if already enrolled
            is_enrolled = db.session.query(users_courses).filter_by(user_id=session["user_id"], course_id=course_id).first() is not None

            # Enroll if it's a free course
            if course.price == 0 and not is_enrolled:
                user = User.query.get(session["user_id"])
                # Add to association table
                stmt = users_courses.insert().values(user_id=user.id, course_id=course.id)
                db.session.execute(stmt)
                db.session.commit()
                return redirect("/account")

            elif is_enrolled:
                return render_template(f"courses/{course_id}.html")

            else:
                if course_id not in session["cart"]:
                    session["cart"].append(course_id)
                    session.modified = True

        elif payment_email:
            user = User.query.get(session["user_id"])
            for c_id in session["cart"]:
                # Check if already enrolled
                is_enrolled = db.session.query(users_courses).filter_by(user_id=user.id, course_id=c_id).first() is not None
                if not is_enrolled:
                    stmt = users_courses.insert().values(user_id=user.id, course_id=c_id)
                    db.session.execute(stmt)
            
            db.session.commit()
            session["cart"] = []
            return redirect("/account")

        # If redeeming a promo code
        elif promo_name:
            promo = Promo.query.filter_by(name=promo_name.upper()).first()

            if promo:
                if promo.id not in session["promo"]:
                    session["promo"].append(promo.id)
                    session.modified = True
                return redirect("/buy")
            else:
                flash("არასწორი პრომო კოდი")
                return redirect("/buy")

    # GET logic
    cart_courses = Course.query.filter(Course.id.in_(session["cart"])).all() if session["cart"] else []
    cart_sum = sum(c.price for c in cart_courses)

    promo_codes = Promo.query.filter(Promo.id.in_(session["promo"])).all() if session["promo"] else []
    promo_sum = sum(p.value for p in promo_codes)

    total = max(0, cart_sum - promo_sum)

    return render_template("pages/courses/buy.html", 
                         cart=cart_courses, 
                         promo=promo_codes, 
                         total=total, 
                         count=len(cart_courses))
