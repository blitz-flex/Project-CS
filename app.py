import os
import re

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from requests import delete, post
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from helpers import login_required, register_required

# Configure application
app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = "./static/images/users"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Main Page
@app.route("/")
def index():

    courses = db.execute("SELECT * FROM courses ORDER BY id DESC LIMIT 3")
    return render_template("index.html", ids = courses)


# About Page
@app.route("/about")
def about():

    return render_template("about.html")


# Users Account
@app.route("/account")
@login_required
def account():

    session["cart"] = []

    users_courses = db.execute("SELECT * FROM users_courses, courses WHERE courses.id = users_courses.course_id AND user_id = ?",
         session["user_id"])

    # See if user has enroled in any course
    if len(users_courses) == 0:

        return render_template("account.html")

    return render_template("account.html", ids = users_courses)



# Buy Page
@app.route("/buy", methods=["GET", "POST"])
@register_required
def buy():

    if "cart" not in session:
        session["cart"] = []

    if "promo" not in session:
        session["promo"] = []

    # POST
    if request.method == "POST":

        id = request.form.get("id")
        payment = request.form.get("email")
        print(payment)
        promo = request.form.get("promo")

        # If buying a course
        if id:

            course = db.execute("SELECT * FROM courses WHERE id = ?", id)
            users_courses = db.execute("SELECT * FROM users_courses WHERE course_id = ? AND user_id = ?", id, session["user_id"])
            price = course[0]["price"]

            # Enroll if it's a free course
            if price == 0 and len(users_courses) == 0:

                db.execute("INSERT INTO users_courses (user_id, course_id) VALUES (?, ?)",
                            session["user_id"], course[0]["id"])

                return redirect("/account")

            # Go to an alreaady owned course
            elif len(users_courses) == 1:

                return render_template(f"courses/{id}.html")

            # Else add item to the cart
            elif id:
                if id not in session["cart"]:
                    session["cart"].append(id)

        elif payment:

            db.execute("INSERT INTO users_courses (user_id, course_id) VALUES (?, ?)",
                        session["user_id"], session["cart"])

            return redirect("/account")

        # If redeeming a promo code
        elif promo:

            promo = promo.upper()
            check_promo = db.execute("SELECT * FROM promo WHERE name = ?", promo)

            try:
                promo_id = check_promo[0]["id"]

            except IndexError:
                return redirect("/buy")

            if len(check_promo) == 1:
                session["promo"].append(promo_id)
                return redirect("/buy")
            else:
                return redirect("/buy")

    # GET
    cart = db.execute("SELECT * FROM courses WHERE id IN (?)", session["cart"])
    cart_sum = db.execute("SELECT SUM(price) FROM courses WHERE id IN (?)", session["cart"])

    promo = db.execute("SELECT * FROM promo WHERE id IN (?)", session["promo"])
    promo_sum = db.execute("SELECT SUM(value) FROM promo WHERE id IN (?)", session["promo"])

    cart_count = db.execute("SELECT COUNT(*) FROM courses WHERE id IN (?)", session["cart"])
    count = cart_count[0]["COUNT(*)"]

    if len(promo) >= 1 and len(cart) >= 1:
        total = cart_sum[0]["SUM(price)"] - promo_sum[0]["SUM(value)"]
        return render_template("buy.html", cart=cart, promo=promo, total=total, count=count)

    elif len(promo) == 0 and len(cart) >= 1:
        total = cart_sum[0]["SUM(price)"]
        return render_template("buy.html", cart=cart, promo=promo, total=total, count=count)

    elif len(promo) == 0 and len(cart) == 0:
        return redirect("/buy")


# Individual course
@app.route("/course", methods=["GET", "POST"])
def course():

    id = int(request.form.get("id"))

    if id == None:
        return redirect("/courses")
    else:
        return render_template(f"courses/{id}.html")


# List all Courses
@app.route("/courses")
def courses():

    # Delete all cart information
    session["cart"] = []

    # Query database for all courses and return them
    courses = db.execute("SELECT * FROM courses")
    return render_template("courses.html", ids = courses)


# FAQ
@app.route("/faq")
def faq():

    return render_template("faq.html")


# Contact
@app.route("/contact")
def contact():

    return render_template("contact.html")


# Courses Info
@app.route("/info", methods=["GET", "POST"])
def info():

    # Delete all cart information
    session["cart"] = []

    # Try to get course ID if exists
    try:
        id = int(request.args.get("id"))
        course = db.execute("SELECT * FROM courses WHERE id = ?", id)
        all_courses = db.execute("SELECT * FROM courses")

        if int(id) < 0 or int(id) > len(all_courses):
            return redirect("/courses")

        return render_template("info.html", ids = course)

    # If it's not a valid input redirect the page
    except ValueError:
        return redirect("/courses")


# Login
@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session["user_id"] = []
    session["cart"] = []
    session["admin"] = []
    session.clear()

    """Login user"""

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Wrong username/password")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["admin"] = rows[0]["admin"]

        return redirect("/account")

    return render_template("login.html")


# Logout
@app.route("/logout")
def logout():

    """Logout user"""

    # Forget any user_id
    session["user_id"] = []
    session["cart"] = []
    session["admin"] = []
    session.clear()

    return redirect("/")


# Check if password is acceptable - has digit, letters and no spaces
def password_check(password):

    a = b = c = False
    for i in range(len(password)):

        if password[i].isspace():
            a = True
        elif password[i].isalpha():
            b = True
        elif password[i].isnumeric():
            c = True

    if a == True:
        flash("Password must contain no spaces")
        return False

    elif b == False or c == False:
        flash("Password must have digits and letters!")
        return False

    elif a == False and b == True and c == True:
        return True


# Register user
@app.route("/signup", methods=["GET", "POST"])
def signup():

    # Forget any user_id
    session["user_id"] = []
    session["cart"] = []
    session["admin"] = []
    session.clear()


    """Register user"""
    username = request.form.get("username")
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("signup.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("signup.html")

        # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return render_template("signup.html")

        # # Ensure the passwords are the same
        elif password != confirmation:
            flash("Passwords dont match")
            return render_template("signup.html")

        # Run password_check function
        else:
            if password_check(password):

                # Query database for username
                rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

                # Check if user is allready taken
                if len(rows) == 1:
                    flash("Username allready exists!")
                    return render_template("signup.html")

                # Create new row in people table
                db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, generate_password_hash(password))

                # Query database for username
                rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

                # Remember which user has logged in
                session["user_id"] = rows[0]["id"]
                session["admin"] = rows[0]["admin"]

                # Redirect user to home page
                return redirect("/courses")

            else:
                return render_template("signup.html")

    else:
        return render_template("signup.html")


# Function to check if file is allowed
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Search bar
@app.route("/search")
def search():

    # GET - Search query and return
    sql = db.execute("SELECT * FROM courses WHERE name LIKE ?", "%" + request.args.get("q") + "%")
    return render_template("search.html", ids=sql)

# Account Settings
@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():

    """Change account settings"""

    # POST
    if request.method == "POST":

        # Ensure the password was submitted
        if not request.form.get("password"):
            flash("Must provide password")
            return redirect("/settings")


        # Delete account
        elif request.form.get("delete") != None:
            # Query database for username
            # Ensure username exists and password is correct
            rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

            if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
                print(rows)
                flash("Wrong Password!")
                return redirect("/settings")

            # Delete account
            else:

                db.execute("DELETE FROM users WHERE id = ?", session["user_id"])
                db.execute("DELETE FROM users_courses WHERE user_id = ?", session["user_id"])

                flash("Account deleted")
                return redirect("/logout")

        # Change User Image
        elif request.form.get("image"):

            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect("/settings")

            file = request.files['file']
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            if file.filename == '':
                flash('No selected file')
                return redirect("/settings")

            if file and allowed_file(file.filename):

                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

                os.rename(os.path.join(app.config["UPLOAD_FOLDER"], filename), os.path.join(app.config["UPLOAD_FOLDER"], str(session["user_id"]) + ".png"))

                db.execute("UPDATE users SET img = ? WHERE id = ?", os.path.join(app.config["UPLOAD_FOLDER"], str(session["user_id"]) + ".png"), session["user_id"])

                return redirect("/settings")

        # Check if users wants to change password
        elif request.form.get("button_pass") != None:

            # Ensure new password was submitted
            if not request.form.get("password_new"):
                flash("Must provide new password")
                return redirect("/settings")

            # Ensure new password confirmation was submitted
            elif not request.form.get("password_confirm"):
                flash("Must confirm new password")
                return redirect("/settings")

            # Ensure new password confirmation was submitted
            elif request.form.get("password_new") != request.form.get("password_confirm"):
                flash("New passwords do not match")
                return redirect("/settings")

            # Run password_check function
            else:
                password_new = request.form.get("password_new")
                if password_check(password_new):

                    # Query database for username
                    rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

                    # Ensure username exists and password is correct
                    if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
                        flash("Wrong Password!")
                        return redirect("/settings")

                    # Insert new password into database
                    db.execute("UPDATE users SET hash = ? WHERE id = ?", generate_password_hash(password_new), session["user_id"])
                    flash("Password changed!")
                    return redirect("/settings")

                else:
                    return redirect("/settings")

    # GET
    else:
        name = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        return render_template("account_settings.html", name=name)