import os
import json
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel, _
from langdetect import detect
from article import db, Article  # استيراد المقالات من article.py

app = Flask(__name__)
app.secret_key = "12345"

# ✅ إعداد قاعدة البيانات
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://ai_news_db_t2em_user:4dddE4EkwvJMycr2BVgAezLaOQVnxbKb@dpg-cumvu81u0jms73b97nc0-a:5432/ai_news_db_t2em"
)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# ✅ إعداد اللغات
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
app.config['LANGUAGES'] = ['en', 'de', 'ar']
babel = Babel(app)

def get_locale():
    return request.args.get('lang') or request.accept_languages.best_match(app.config['LANGUAGES'])

babel.init_app(app, locale_selector=get_locale)

# ✅ تحميل المقالات من `news.json` عند بدء التطبيق
def load_articles_from_json():
    if os.path.exists("news.json"):
        with open("news.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            return data.get("articles", [])
    return []

# ✅ إدخال المقالات من `news.json` إلى قاعدة البيانات عند التشغيل
def insert_articles_from_json():
    articles = load_articles_from_json()
    with app.app_context():
        for article in articles:
            exists = Article.query.filter_by(title=article["title"]).first()
            if not exists:
                new_article = Article(
                    title=article["title"],
                    content=article["content"],
                    image=article.get("image", "https://via.placeholder.com/300"),
                    category=article["category"]
                )
                db.session.add(new_article)
        db.session.commit()

# ✅ إنشاء الجداول وإضافة المقالات إذا لم تكن موجودة
with app.app_context():
    db.create_all()
    insert_articles_from_json()

# ✅ API لاسترجاع المقالات من قاعدة البيانات
@app.route("/api/get_articles/<category>/<lang>", methods=["GET"])
def get_articles(category, lang):
    articles = Article.query.filter_by(category=category, language=lang).order_by(Article.id.desc()).all()
    articles_list = [article.to_dict() for article in articles]
    return jsonify({"articles": articles_list})

# ✅ تشغيل التطبيق
if __name__ == "__main__":
    app.run(debug=True)
