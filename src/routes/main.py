from flask import Blueprint, render_template, request, flash, redirect, url_for
from src.models.course import Course

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def index():
    courses = Course.query.limit(3).all()
    return render_template("pages/main/index.html", courses=courses)

@main_bp.route("/faq")
def faq():
    return render_template("pages/main/faq.html")

@main_bp.route("/search")
def search():
    query = request.args.get("q", "")
    if query:
        # Case-insensitive search for course names
        results = Course.query.filter(Course.name.ilike(f"%{query}%")).all()
    else:
        results = []
    return render_template("pages/main/search.html", ids=results, query=query)

@main_bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        subject = request.form.get("subject")
        message = request.form.get("message")
        
        if not name or not email or not subject or not message:
            flash("გთხოვთ შეავსოთ ყველა ველი", "error")
            return render_template("pages/main/contact.html")

        flash("თქვენი შეტყობინება წარმატებით გაიგზავნა! ჩვენ მალე დაგიკავშირდებით.", "success")
        return redirect(url_for("main.contact"))
    
    return render_template("pages/main/contact.html")
