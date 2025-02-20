from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel
import os
from dotenv import load_dotenv
from datetime import datetime

# ✅ Load environment variables
load_dotenv()

# ✅ Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "123456")

# ✅ Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "postgresql://ai_news_db_t2em_user:4dddE4EkwvJMycr2BVgAezLaOQVnxbKb@dpg-cumvu81u0jms73b97nc0-a.oregon-postgres.render.com:5432/ai_news_db_t2em")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ✅ Localization Setup
babel = Babel(app)
app.config["BABEL_DEFAULT_LOCALE"] = "en"
app.config["LANGUAGES"] = ["en", "ar"]

def get_locale():
    return session.get("lang", request.accept_languages.best_match(app.config["LANGUAGES"]))

babel.init_app(app, locale_selector=get_locale)

@app.context_processor
def inject_locale():
    return dict(get_locale=get_locale)

# ✅ Define Article Model
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(100))
    author = db.Column(db.String(100))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    url = db.Column(db.String(255), nullable=False)
    publishedAt = db.Column(db.String(50))
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), default="https://via.placeholder.com/600")

# ✅ Ensure database is set up
with app.app_context():
    db.create_all()

# ✅ Home Route - Fetch and Display Articles
@app.route("/")
def home():
    articles = Article.query.order_by(Article.publishedAt.desc()).all()
    return render_template("index.html", articles=articles)

# ✅ Language Switching Route
@app.route("/set_language")
def set_language():
    lang = request.args.get("lang", "en")
    if lang in app.config["LANGUAGES"]:
        session["lang"] = lang
    return redirect(request.referrer or url_for("home"))

# ✅ Run the App
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
