from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_babel import Babel
import os
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy import text

#  Load environment variables
load_dotenv()

#  Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "123456")

#  Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "postgresql://ai_news_db_user:4dddE4EkwvJMycr2BVgAezLaOQVnxbKb@dpg-cumvu81u0jms73b97nc0-a:5432/ai_news_db",
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#  Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)

#  Define Models
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255))
    category = db.Column(db.String(100))
   # language = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # ✅ Automatically set if missing

class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(255), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)


with app.app_context():
    db.create_all()
    
    #  Check if `created_at` column is missing and add it dynamically
    with db.engine.connect() as connection:
        result = connection.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'article'"))
        columns = {row[0] for row in result}
        if "created_at" not in columns:
            connection.execute(text("ALTER TABLE article ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;"))
            print(" Column `created_at` was missing and has been added.")


#  Flask-Babel for Multi-language Support
babel = Babel(app)
app.config["BABEL_DEFAULT_LOCALE"] = "en"
app.config["BABEL_TRANSLATION_DIRECTORIES"] = "translations"
app.config["LANGUAGES"] = ["en", "ar"]

def get_locale():
    return session.get("lang", request.accept_languages.best_match(app.config["LANGUAGES"]))

babel.init_app(app, locale_selector=get_locale)

@app.context_processor
def inject_locale():
    return dict(get_locale=get_locale)

@app.route("/")
def home():
    try:
        db.session.rollback()  # التأكد من عدم وجود جلسات فاشلة
        
        with db.engine.connect() as connection:
            result = connection.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'article'"))
            columns = {row[0] for row in result}

        if "created_at" in columns:
            print("✅ `created_at` موجود، سيتم ترتيب المقالات.")
            articles = Article.query.order_by(Article.created_at.desc()).limit(10).all()
        else:
            print("⚠️ Warning: Column `created_at` is missing! Fetching articles without ordering.")
            articles = Article.query.limit(10).all()

    except Exception as e:
        db.session.rollback()
        print(f"⚠️ Error fetching articles: {e}")
        articles = []

    return render_template("index.html", articles=articles)


#  Admin Login
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == "abo" and password == "1234":
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            return " Invalid login!", 403
    return render_template("admin_login.html")

#  Admin Dashboard
@app.route("/admin")
def admin_dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    articles = Article.query.all()
    sections = Section.query.all()
    pages = Page.query.all()
    return render_template("admin_dashboard.html", articles=articles, sections=sections, pages=pages)

#  API to Add Article
@app.route("/admin/add_article", methods=["POST"])
def add_article():
    if not session.get("admin"):
        return jsonify({"error": "Unauthorized!"}), 403

    data = request.json
    new_article = Article(
        title=data["title"],
        content=data["content"],
        image=data["image"],
        category=data["category"],
      #  language=data["language"],
    )
    db.session.add(new_article)
    db.session.commit()
    return jsonify({"message": " Article added successfully!"}), 201

#  API to Delete Article
@app.route("/admin/delete_article/<int:id>", methods=["DELETE"])
def delete_article(id):
    if not session.get("admin"):
        return jsonify({"error": "Unauthorized!"}), 403

    article = Article.query.get(id)
    if article:
        db.session.delete(article)
        db.session.commit()
        return jsonify({"message": "🗑️ Article deleted!"})
    return jsonify({"error": "❌ Article not found!"}), 404

# ✅ API to Add Page
@app.route("/admin/add_page", methods=["POST"])
def add_page():
    if not session.get("admin"):
        return jsonify({"error": "Unauthorized!"}), 403

    data = request.json
    new_page = Page(title=data["title"], content=data["content"], slug=data["slug"])
    db.session.add(new_page)
    db.session.commit()
    return jsonify({"message": "✅ Page added!"}), 201

# ✅ Set Language Route
@app.route("/set_language")
def set_language():
    lang = request.args.get("lang", "en")
    if lang in app.config["LANGUAGES"]:
        session["lang"] = lang
    return redirect(request.referrer or url_for("home"))

# ✅ Run the App
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
