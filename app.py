from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel
import os
from dotenv import load_dotenv
from datetime import datetime
from flask_migrate import Migrate

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Secret Key (should be stored securely, not hardcoded)
app.secret_key = "ABO8888"

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "postgresql://ai_news_db_t2em_user:4dddE4EkwvJMycr2BVgAezLaOQVnxbKb@dpg-cumvu81u0jms73b97nc0-a.oregon-postgres.render.com/ai_news_db_t2em")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Import models AFTER initializing db
from article import Article  # Ensure this import is correct and the Article model is defined

# Initialize Babel
babel = Babel(app)

# Supported languages
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
app.config['LANGUAGES'] = ['en', 'de', 'ar']

# Function to determine the preferred language
def get_locale():
    if "lang" in request.args:
        session["lang"] = request.args["lang"]
    return session.get("lang", request.accept_languages.best_match(app.config["LANGUAGES"]))

babel.init_app(app, locale_selector=get_locale)

# Home route that fetches articles based on selected language
@app.route("/")
def home():
    lang = get_locale()
    try:
        with app.app_context():  # Ensure application context
            articles = Article.query.filter_by(language=lang).order_by(Article.id.desc()).all()
        return render_template("index.html", articles=articles, lang=lang)
    except Exception as e:
        return str(e), 500  # Return error message with a 500 status code

# API to get all articles
@app.route("/api/articles", methods=["GET"])
def get_articles():
    """Fetch all articles from the database and return as JSON."""
    try:
        with app.app_context():  # Ensure application context
            articles = Article.query.all()
        return jsonify([article.to_dict() for article in articles])
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return error message with a 500 status code

# Configure debug mode based on environment variable
app.config["DEBUG"] = os.getenv("DEBUG", "False").lower() == "true"

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])
