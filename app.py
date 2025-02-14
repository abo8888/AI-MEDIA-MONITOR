from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from langdetect import detect

# ✅ Initialize Flask App
app = Flask(__name__)
app.secret_key = "your_secret_key"

# ✅ Configure PostgreSQL Database (Use Render Database URL)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@host:port/dbname")  
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ✅ Initialize Database
db = SQLAlchemy(app)

# ✅ Define Article Model (For PostgreSQL)
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255))
    category = db.Column(db.String(100))
    language = db.Column(db.String(10))

# ✅ Create Database Tables
with app.app_context():
    db.create_all()

# ✅ Detect Language Function
def detect_language(text):
    """Detect language of an article."""
    try:
        lang = detect(text)
        return "ar" if lang == "ar" else "en"
    except:
        return "unknown"

# ✅ API to Upload Articles
@app.route('/api/upload_articles', methods=["POST"])
def upload_articles():
    """Receive and store articles in PostgreSQL database."""
    data = request.get_json()
    if not data or "articles" not in data:
        return jsonify({"error": "Invalid request, 'articles' key is missing"}), 400

    for article in data["articles"]:
        new_article = Article(
            title=article["title"],
            content=article["content"],
            image=article["image"],
            category=article["category"],
            language=detect_language(article["content"])
        )
        db.session.add(new_article)

    db.session.commit()
    return jsonify({"message": "Articles saved to database!"}), 201

# ✅ API to Retrieve Articles
@app.route('/api/get_articles', methods=["GET"])
def get_articles():
    """Fetch articles from PostgreSQL database."""
    articles = Article.query.all()
    articles_list = [
        {"title": a.title, "content": a.content, "image": a.image, "category": a.category, "language": a.language}
        for a in articles
    ]
    return jsonify({"articles": articles_list})

# ✅ Homepage with Language Toggle
@app.route('/')
def home():
    lang = request.args.get('lang', 'en')  # Default language is English
    articles_ar = Article.query.filter_by(language="ar").all()
    articles_en = Article.query.filter_by(language="en").all()

    return render_template("index.html", news_ar=articles_ar, news_en=articles_en, lang=lang)

# ✅ Admin Dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin panel to manage articles."""
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    articles_ar = Article.query.filter_by(language="ar").all()
    articles_en = Article.query.filter_by(language="en").all()

    return render_template("admin_dashboard.html", news_ar=articles_ar, news_en=articles_en)

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/admin/login', methods=["GET", "POST"])
def admin_login():
    """Admin login page"""
    if request.method == "POST":
        username = request.form["abo"]
        password = request.form["admin"]
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            return "🚨 Login failed, please check your credentials!", 403

    return render_template("admin_login.html")
