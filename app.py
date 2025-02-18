from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel
import os
from dotenv import load_dotenv
from datetime import datetime
from flask import jsonify
from article import Article


# ✅ Load environment variables
load_dotenv()

# ✅ Initialize Flask app
app = Flask(__name__)
babel = Babel(app)

# ✅ Security settings
app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")

# ✅ Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ✅ Initialize SQLAlchemy
db = SQLAlchemy(app)

# ✅ Supported languages configuration
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
app.config['LANGUAGES'] = ['en', 'de', 'ar']

# ✅ Function to determine the preferred language
def get_locale():
    if "lang" in request.args:
        session["lang"] = request.args["lang"]
    return session.get("lang", request.accept_languages.best_match(app.config["LANGUAGES"]))

# ✅ Initialize Babel with the language selector
babel.init_app(app, locale_selector=get_locale)

# ✅ Make `get_locale` available in all templates
@app.context_processor
def inject_get_locale():
    return dict(get_locale=get_locale)

# ✅ Article model with timestamps
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(500), nullable=True)
    category = db.Column(db.String(50), nullable=False)
    language = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

# ✅ Home route that fetches articles based on selected language
@app.route("/")
def home():
    lang = get_locale()
    articles = Article.query.filter_by(language=lang).order_by(Article.id.desc()).all()
    return render_template("index.html", articles=articles, lang=lang)

# ✅ Configure debug mode based on environment variable
app.config["DEBUG"] = os.getenv("DEBUG", "False").lower() == "true"
@app.route("/api/articles", methods=["GET"])

def get_articles():
    """Fetch all articles from the database and return as JSON."""
    articles = Article.query.all()
    return jsonify([article.to_dict() for article in articles])

# ✅ Run the Flask app
if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])
