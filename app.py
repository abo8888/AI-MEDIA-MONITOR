from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel
from langdetect import detect
import os

# ✅ إعداد تطبيق Flask
app = Flask(__name__)
babel = Babel(app)

app.secret_key = "12345"

# ✅ تكوين قاعدة البيانات
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "postgresql://ai_news_db_t2em_user:4dddE4EkwvJMycr2BVgAezLaOQVnxbKb@dpg-cumvu81u0jms73b97nc0-a.oregon-postgres.render.com/ai_news_db_t2em"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ✅ إعداد اللغات المدعومة
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
app.config['LANGUAGES'] = ['en', 'de', 'ar']

# ✅ دالة اختيار اللغة
def get_locale():
    return request.args.get('lang') or request.accept_languages.best_match(app.config['LANGUAGES'])

babel.init_app(app, locale_selector=get_locale)

# ✅ جعل `get_locale` متاحًا في جميع القوالب
@app.context_processor
def inject_get_locale():
    return dict(get_locale=get_locale)

# ✅ الصفحة الرئيسية
@app.route("/")
def home():
    news = db.session.query(Article).filter_by(category="news", language=get_locale()).order_by(Article.id.desc()).all()
    return render_template("index.html", news=news)

# ✅ تشغيل التطبيق
if __name__ == "__main__":
    app.run(debug=True)
