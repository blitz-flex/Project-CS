from flask import Blueprint, render_template, request, session, redirect, flash
from src.extensions import db
from src.models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("უნდა შეიყვანოთ მომხმარებლის სახელი და პაროლი")
            return render_template("pages/auth/login.html")

        # Query database using SQLAlchemy
        user = User.query.filter_by(username=username).first()

        # Ensure username exists and password is correct
        if user is None or not user.check_password(password):
            flash("არასწორი მომხმარებლის სახელი ან პაროლი")
            return render_template("pages/auth/login.html")

        # Remember which user has logged in
        session["user_id"] = user.id
        if user.admin:
            session["admin"] = True

        return redirect("/")

    return render_template("pages/auth/login.html")

@auth_bp.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    return redirect("/")

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username or not password or not confirmation:
            flash("შეავსეთ ყველა ველი")
            return render_template("pages/auth/signup.html")

        if password != confirmation:
            flash("პაროლები არ ემთხვევა")
            return render_template("pages/auth/signup.html")

        # Check if username exists
        if User.query.filter_by(username=username).first():
            flash("მომხმარებლის სახელი დაკავებულია")
            return render_template("pages/auth/signup.html")

        # Create new user object
        new_user = User(username=username)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        session["user_id"] = new_user.id
        flash("რეგისტრაცია წარმატებით დასრულდა!")
        return redirect("/")

    return render_template("pages/auth/signup.html")
