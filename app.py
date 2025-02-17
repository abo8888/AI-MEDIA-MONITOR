from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel
import os

# ✅ إنشاء تطبيق Flask
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

# ✅ نموذج للمقالات
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(500), nullable=True)
    category = db.Column(db.String(50), nullable=False)
    language = db.Column(db.String(10), nullable=False)

# ✅ الصفحة الرئيسية
@app.route("/")
def home():
    lang = get_locale()
    articles = Article.query.filter_by(language=lang).order_by(Article.id.desc()).all()
    return render_template("index.html", articles=articles, lang=lang)

# ✅ تشغيل التطبيق
if __name__ == "__main__":
    app.run(debug=True)
