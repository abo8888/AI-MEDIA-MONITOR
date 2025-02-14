from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pandas as pd
import os
from langdetect import detect
import json

# ✅ Initialize Flask App
app = Flask(__name__)
app.secret_key = "your_secret_key"

# ✅ Define File Paths
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
CSV_FILE_AR = os.path.join(UPLOAD_FOLDER, "articles_ar.csv")
CSV_FILE_EN = os.path.join(UPLOAD_FOLDER, "articles_en.csv")

# ✅ Admin Credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "securepassword"

# ✅ Detect Language Function
def detect_language(text):
    """Detect language of an article."""
    try:
        lang = detect(text)
        return "ar" if lang == "ar" else "en"
    except:
        return "unknown"

# ✅ Load Articles by Language
def load_articles():
    """Load articles and classify them by language."""
    articles = {"ar": [], "en": []}

    if os.path.exists(CSV_FILE_AR):
        df_ar = pd.read_csv(CSV_FILE_AR, encoding="utf-8-sig")
        if {"title", "content", "image", "category"}.issubset(df_ar.columns):
            articles["ar"] = df_ar.to_dict(orient="records")

    if os.path.exists(CSV_FILE_EN):
        df_en = pd.read_csv(CSV_FILE_EN, encoding="utf-8-sig")
        if {"title", "content", "image", "category"}.issubset(df_en.columns):
            articles["en"] = df_en.to_dict(orient="records")

    return articles

# ✅ API Endpoint to Upload Articles
@app.route('/api/upload_articles', methods=["POST"])
def upload_articles():
    """API to receive and store articles."""
    data = request.get_json()

    if not data or "articles" not in data:
        return jsonify({"error": "Invalid request, 'articles' key is missing"}), 400

    # ✅ Save articles to JSON file
    with open("uploaded_articles.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return jsonify({"message": "Articles uploaded successfully!"}), 201

# ✅ Homepage with Language Toggle
@app.route('/')
def home():
    """Render homepage with articles in English and Arabic."""
    lang = request.args.get('lang', 'en')  # Default language is English
    articles = load_articles()
    return render_template("index.html", news_ar=articles["ar"], news_en=articles["en"], lang=lang)

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin panel to manage articles."""
    if not session.get("admin"):
        return redirect(url_for("admin_login"))  # ✅ تأكد من أن هذا يعمل

    articles = load_articles()
    return render_template("admin_dashboard.html", news_ar=articles["ar"], news_en=articles["en"])


# ✅ Run Flask App
if __name__ == '__main__':
    app.run(debug=True)

@app.route('/admin/login', methods=["GET", "POST"])
def admin_login():
    """Admin login page"""
    if request.method == "POST":
        username = request.form["abo"]
        password = request.form["admin"]
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            return "🚨 Login failed, please check your credentials!", 403

    return render_template("admin_login.html")
