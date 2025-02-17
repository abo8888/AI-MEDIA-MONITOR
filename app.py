import os
import json
import pandas as pd
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel, _
from langdetect import detect
from article import db, Article  # استيراد المقالات من article.py

# ✅ إعداد تطبيق Flask
app = Flask(__name__)
app.secret_key = "12345"

# ✅ تكوين قاعدة البيانات (متوافق مع منصة Render)
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://ai_news_db_t2em_user:4dddE4EkwvJMycr2BVgAezLaOQVnxbKb@dpg-cumvu81u0jms73b97nc0-a:5432/ai_news_db_t2em"
)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)  # ✅ تهيئة قاعدة البيانات

# ✅ إنشاء الجداول داخل قاعدة البيانات عند بدء التطبيق
with app.app_context():
    db.create_all()

# ✅ إعداد اللغات المدعومة
app.config['BABEL_DEFAULT_LOCALE'] = 'en'  # اللغة الافتراضية
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'  # مكان حفظ الترجمات
app.config['LANGUAGES'] = ['en', 'de', 'ar']
babel = Babel(app)

# ✅ دالة اختيار اللغة
def get_locale():
    return request.args.get('lang') or request.accept_languages.best_match(app.config['LANGUAGES'])

babel.init_app(app, locale_selector=get_locale)

# ✅ وظيفة لاكتشاف لغة المقال تلقائيًا
def detect_language(text):
    try:
        lang = detect(text)
        return lang if lang in ["ar", "en", "de"] else "en"
    except Exception as e:
        print(f"Error detecting language: {e}")
        return "unknown"

# ✅ الصفحة الرئيسية
@app.route("/")
def home():
    lang = get_locale()  # تحديد اللغة المختارة
    news = Article.query.filter_by(category="news", language=lang).order_by(Article.id.desc()).all()
    return render_template("index.html", news=news, lang=lang)

# 🚀 **API لنشر المقالات في قاعدة البيانات**
@app.route("/api/publish", methods=["POST"])
def publish_article():
    data = request.json
    if not data or "title" not in data or "content" not in data or "image" not in data:
        return jsonify({"error": "❌ البيانات غير مكتملة!"}), 400

    # ✅ إنشاء مقال جديد وإضافته إلى قاعدة البيانات
    new_article = Article(
        title=data["title"],
        content=data["content"],
        image=data["image"],
        category=data.get("category", "news"),
        language=detect_language(data["content"])
    )

    try:
        db.session.add(new_article)
        db.session.commit()
        return jsonify({"message": f"✅ تم نشر المقال: {data['title']}"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"❌ فشل نشر المقال: {str(e)}"}), 500

# ✅ API لاسترجاع المقالات حسب الفئة واللغة
@app.route("/api/get_articles/<category>/<lang>", methods=["GET"])
def get_articles(category, lang):
    articles = Article.query.filter_by(category=category, language=lang).order_by(Article.id.desc()).all()
    articles_list = [
        {"title": a.title, "content": a.content, "image": a.image, "category": a.category, "language": a.language}
        for a in articles
    ]
    return jsonify({"articles": articles_list})

# ✅ تشغيل التطبيق
if __name__ == "__main__":
    app.run(debug=True)
