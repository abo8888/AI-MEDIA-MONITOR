import os
import pandas as pd
import requests
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from langdetect import detect
from sqlalchemy import create_engine

# ✅ إعداد تطبيق Flask
app = Flask(__name__)
app.secret_key = "12345"

# ✅ الحصول على عنوان قاعدة البيانات من المتغيرات البيئية أو استخدام العنوان المباشر
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://ai_news_db_t2em_user:4dddE4EkwvJMycr2BVgAezLaOQVnxbKb@dpg-cumvu81u0jms73b97nc0-a.oregon-postgres.render.com:5432/ai_news_db_t2em")

# ✅ تكوين قاعدة البيانات
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ✅ تعريف نموذج المقال
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255))
    category = db.Column(db.String(100))
    language = db.Column(db.String(10))

# ✅ إنشاء الجداول عند بدء التشغيل
with app.app_context():
    db.create_all()

# ✅ وظيفة لاكتشاف اللغة
def detect_language(text):
    """Detect language of an article."""
    try:
        lang = detect(text)
        return "ar" if lang == "ar" else "en"
    except:
        return "unknown"

# ✅ الصفحة الرئيسية
@app.route("/")
def home():
    return "🎉 التطبيق يعمل بنجاح!"

# ✅ API لإضافة المقالات إلى قاعدة البيانات
@app.route('/api/upload_articles', methods=["POST"])
def upload_articles():
    """استقبال وتخزين المقالات في قاعدة البيانات."""
    data = request.get_json()
    if not data or "articles" not in data:
        return jsonify({"error": "❌ البيانات غير صحيحة!"}), 400

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
    return jsonify({"message": "✅ تم حفظ المقالات بنجاح!"}), 201

# ✅ API لاسترجاع المقالات من قاعدة البيانات
@app.route('/api/get_articles', methods=["GET"])
def get_articles():
    """جلب المقالات المخزنة في قاعدة البيانات."""
    articles = Article.query.all()
    articles_list = [
        {"title": a.title, "content": a.content, "image": a.image, "category": a.category, "language": a.language}
        for a in articles
    ]
    return jsonify({"articles": articles_list})

# ✅ API لنشر المقالات (إضافة مقالة جديدة)
@app.route('/api/publish', methods=['POST'])
def publish_article():
    """نشر المقالات على الموقع وإضافتها إلى قاعدة البيانات."""
    data = request.json
    if "title" in data and "article" in data and "image_url" in data:
        new_article = Article(
            title=data["title"],
            content=data["article"],
            image=data["image_url"],
            language=detect_language(data["article"])
        )
        db.session.add(new_article)
        db.session.commit()
        return jsonify({"message": "✅ تم نشر المقال بنجاح!"}), 200
    else:
        return jsonify({"error": "❌ البيانات غير مكتملة!"}), 400
@app.route('/api/get_articles_sql', methods=['GET'])
def get_articles_sql():
    query = "SELECT * FROM articles ORDER BY created_at DESC;"
    result = engine.execute(query)
    articles = [dict(row) for row in result]
    return jsonify({"articles": articles})

# ✅ تشغيل التطبيق
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
