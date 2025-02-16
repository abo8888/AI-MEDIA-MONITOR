import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from langdetect import detect

# ✅ إعداد تطبيق Flask
app = Flask(__name__)
app.secret_key = "12345"

# ✅ تكوين قاعدة البيانات
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://ai_news_db_t2em_user:4dddE4EkwvJMycr2BVgAezLaOQVnxbKb@dpg-cumvu81u0jms73b97nc0-a:5432/ai_news_db_t2em"
)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ✅ نموذج المقال
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255))
    category = db.Column(db.String(100), nullable=False)
    language = db.Column(db.String(10), nullable=False)

# ✅ إنشاء الجداول
with app.app_context():
    db.create_all()

# ✅ وظيفة لاكتشاف اللغة
def detect_language(text):
    try:
        lang = detect(text)
        return "ar" if lang == "ar" else "en"
    except:
        return "unknown"

# ✅ الصفحة الرئيسية
@app.route("/")
def home():
    lang = request.args.get("lang", "en")
    news = Article.query.filter_by(category="news", language=lang).all()
    return render_template("index.html", news=news, lang=lang)

# ✅ API نشر المقالات
@app.route("/api/publish", methods=["POST"])
def publish_article():
    data = request.json
    if not data or "title" not in data or "content" not in data or "image" not in data:
        return jsonify({"error": "❌ البيانات غير مكتملة!"}), 400

    new_article = Article(
        title=data["title"],
        content=data["content"],
        image=data["image"],
        category=data.get("category", "news"),
        language=detect_language(data["content"])
    )

    db.session.add(new_article)
    db.session.commit()

    return jsonify({"message": f"✅ تم نشر المقال: {data['title']}"}), 201

# ✅ API لاسترجاع المقالات
@app.route("/api/get_articles/<category>/<lang>", methods=["GET"])
def get_articles(category, lang):
    articles = Article.query.filter_by(category=category, language=lang).all()
    articles_list = [
        {"title": a.title, "content": a.content, "image": a.image, "category": a.category, "language": a.language}
        for a in articles
    ]
    return jsonify({"articles": articles_list})

# ✅ تشغيل التطبيق
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
