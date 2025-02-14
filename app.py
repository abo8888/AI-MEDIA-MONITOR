from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pandas as pd
import os
from langdetect import detect

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

# ✅ Homepage with Language Toggle
@app.route('/')
def home():
    lang = request.args.get('lang', 'en')  # Default language is English
    articles = load_articles()
    return render_template("index.html", news_ar=articles["ar"], news_en=articles["en"], lang=lang)

# ✅ Upload Articles Automatically with Language Detection
@app.route('/admin/upload', methods=["POST"])
def upload_articles():
    """Upload CSV file and classify articles by language."""
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    if "file" not in request.files:
        return "🚨 No file uploaded!", 400

    file = request.files["file"]
    if file.filename.endswith(".csv"):
        df = pd.read_csv(file, encoding="utf-8-sig")

        if {"title", "content", "image", "category"}.issubset(df.columns):
            df["language"] = df["content"].apply(detect_language)

            df_ar = df[df["language"] == "ar"].drop(columns=["language"])
            df_en = df[df["language"] == "en"].drop(columns=["language"])

            df_ar.to_csv(CSV_FILE_AR, index=False, encoding="utf-8-sig")
            df_en.to_csv(CSV_FILE_EN, index=False, encoding="utf-8-sig")

    return redirect(url_for("admin_dashboard"))

# ✅ Admin Dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin panel to manage articles."""
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    articles = load_articles()
    return render_template("admin_dashboard.html", news_ar=articles["ar"], news_en=articles["en"])

# ✅ Run Flask App
if __name__ == '__main__':
    app.run(debug=True)
