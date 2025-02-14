from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pandas as pd
import os
from langdetect import detect  # 🔍 مكتبة تحديد اللغة

# ✅ إعداد Flask
app = Flask(__name__)
app.secret_key = "your_secret_key"  # ⚠️ غيّر هذا المفتاح ليكون أكثر أمانًا

# ✅ تحديد مسار الملفات المخزنة
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
CSV_FILE_AR = os.path.join(UPLOAD_FOLDER, "articles_ar.csv")
CSV_FILE_EN = os.path.join(UPLOAD_FOLDER, "articles_en.csv")

# ✅ بيانات تسجيل الدخول للمشرف
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "securepassword"  # ⚠️ استخدم كلمة مرور قوية

# ✅ وظيفة التعرف على اللغة
def detect_language(text):
    """ تحديد لغة المقال تلقائيًا """
    try:
        lang = detect(text)
        return "ar" if lang == "ar" else "en"
    except:
        return "unknown"

# ✅ تحميل المقالات حسب اللغة
def load_articles():
    """ تحميل المقالات وتقسيمها حسب اللغة """
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

# ✅ الصفحة الرئيسية
@app.route('/')
def home():
    articles = load_articles()
    return render_template("index.html", news_ar=articles["ar"], news_en=articles["en"])

# ✅ رفع المقالات تلقائيًا وتحديد اللغة
@app.route('/admin/upload', methods=["POST"])
def upload_articles():
    """ تحميل ملف CSV وتحديد اللغة تلقائيًا """
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    if "file" not in request.files:
        return "🚨 لم يتم رفع أي ملف!", 400

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

# ✅ لوحة التحكم
@app.route('/admin/dashboard')
def admin_dashboard():
    """ عرض لوحة التحكم للمشرف """
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    articles = load_articles()
    return render_template("admin_dashboard.html", news_ar=articles["ar"], news_en=articles["en"])

# ✅ تشغيل التطبيق
if __name__ == '__main__':
    app.run(debug=True)
