from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel
import os
from dotenv import load_dotenv
from datetime import datetime
from flask_migrate import Migrate

# Load environment variables
load_dotenv()

# Initialize database and migration
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # Secret Key (should be stored securely)
    app.secret_key = os.getenv("SECRET_KEY", "123456")

    # Database Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "postgresql://ai_news_db_t2em_user:4dddE4EkwvJMycr2BVgAezLaOQVnxbKb@dpg-cumvu81u0jms73b97nc0-a.oregon-postgres.render.com/ai_news_db_t2em")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize database and migration
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models after initializing db
    from article import Article

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
            articles = Article.query.filter_by(language=lang).order_by(Article.id.desc()).all()
            return render_template("index.html", articles=articles, lang=lang)
        except Exception as e:
            return str(e), 500

    # API to get all articles
    @app.route("/api/articles", methods=["GET"])
    def get_articles():
        """Fetch all articles from the database and return as JSON."""
        try:
            articles = Article.query.all()
            return jsonify([article.to_dict() for article in articles])
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Configure debug mode based on environment variable
    app.config["DEBUG"] = os.getenv("DEBUG", "False").lower() == "true"

    return app

