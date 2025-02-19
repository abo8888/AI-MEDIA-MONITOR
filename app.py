from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel
import os
from datetime import datetime
from flask_migrate import Migrate

# Initialize Flask app
app = Flask(__name__)
babel = Babel(app)

# Security settings
app.secret_key = "12345"

# Database Configuration (Hardcoded URL)
DATABASE_URL = "postgresql://ai_news_db_t2em_user:4dddE4EkwvJMycr2BVgAezLaOQVnxbKb@dpg-cumvu81u0jms73b97nc0-a:5432/ai_news_db_t2em"
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy (Before importing models)
db = SQLAlchemy()
migrate = Migrate()

# Register `db` with the Flask app
db.init_app(app)
migrate.init_app(app, db)

# Now, import models AFTER initializing db
with app.app_context():  # Ensure app context is active
    from article import Article  

# Supported languages configuration
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
app.config['LANGUAGES'] = ['en', 'de', 'ar']

# Function to determine the preferred language
def get_locale():
    if "lang" in request.args:
        session["lang"] = request.args["lang"]
    return session.get("lang", request.accept_languages.best_match(app.config["LANGUAGES"]))

# Initialize Babel with the language selector
babel.init_app(app, locale_selector=get_locale)

# Make `get_locale` available in all templates
@app.context_processor
def inject_get_locale():
    return dict(get_locale=get_locale)

# Home route that fetches articles based on selected language
@app.route("/")
def home():
    lang = get_locale()
    with app.app_context():  # Ensure app context is active
        articles = Article.query.filter_by(language=lang).order_by(Article.id.desc()).all()
    return render_template("index.html", articles=articles, lang=lang)

# API to get all articles
@app.route("/api/articles", methods=["GET"])
def get_articles():
    """Fetch all articles from the database and return as JSON."""
    with app.app_context():
        articles = Article.query.all()
    return jsonify([article.to_dict() for article in articles])

# Configure debug mode based on environment variable
app.config["DEBUG"] = os.getenv("DEBUG", "False").lower() == "true"

# Run the Flask app
if __name__ == "__main__":
    with app.app_context():  # Ensure app context before running
        db.create_all()  # Create tables if they don't exist
    app.run(debug=app.config["DEBUG"])
