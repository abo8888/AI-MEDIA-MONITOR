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

# ✅ Use External Database URL from Render
DATABASE_URL = "postgresql://ai_news_db_t2em_user:4dddE4EkwvJMycr2BVgAezLaOQVnxbKb@dpg-cumvu81u0jms73b97nc0-a.oregon-postgres.render.com:5432/ai_news_db_t2em"

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy
db = SQLAlchemy()
migrate = Migrate(app, db)
db.init_app(app)

# Import models AFTER initializing db
with app.app_context():
    from article import Article  

# Supported languages configuration
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
app.config['LANGUAGES'] = ['en', 'de', 'ar']



# Define the locale selector function
def get_locale():
    # You can customize the logic here to determine the user's locale
    return request.accept_languages.best_match(['en', 'es', 'de'])

# Initialize Babel with the locale selector
babel = Babel(app, locale_selector=get_locale)

def babel_locale_selector():
    return get_locale()

@app.context_processor
def inject_get_locale():
    """Ensures `get_locale` is available in Jinja2 templates."""
    return dict(get_locale=get_locale)

# Home route
@app.route("/")
def home():
    lang = get_locale()
    articles = Article.query.filter_by(language=lang).order_by(Article.id.desc()).all()
    return render_template("index.html", articles=articles, lang=lang)

# API to get all articles
@app.route("/api/articles", methods=["GET"])
def get_articles():
    articles = Article.query.all()
    return jsonify([article.to_dict() for article in articles])

# Configure debug mode
app.config["DEBUG"] = os.getenv("DEBUG", "False").lower() == "true"

# Run the Flask app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(debug=app.config["DEBUG"])
