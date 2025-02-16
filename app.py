import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from langdetect import detect

# ✅ إعداد تطبيق Flask
app = Flask(__name__)
app.secret_key = "12345"

# ✅ الحصول على عنوان قاعدة البيانات من المتغيرات البيئية أو استخدام العنوان المباشر
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://ai_news_db_t2em_user:4dddE4EkwvJMycr2BVgAezLaOQVnxbKb@dpg-cumvu81u0jms73b97nc0-a.oregon-postgres.render.com:5432/ai_news_db_t2em"
)

# ✅ تكوين قاعدة البيانات
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# ✅ تعريف نموذج المقال
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255))
    category = db.Column(db.String(100), nullable=False)  # (الأخبار، الدراسات، الميديا)
    language = db.Column(db.String(10), nullable=False)  # (ar, en)

# ✅ إنشاء الجداول عند بدء التشغيل
with app.app_context():
    db.create_all()

# ✅ وظيفة لاكتشاف اللغة
def detect_language(text):
    """Detect language of an article."""
    try:
        lang = detect(text)
        return "ar" if lang == "ar" else "en"
    except:
        return "unknown"

# ✅ الصفحة الرئيسية (تعرض الأخبار والدراسات والميديا)
@app.route("/")
def home():
    lang = request.args.get("lang", "en")  # الافتراضي الإنجليزية
    news = Article.query.filter_by(category="news", language=lang).all()
    studies = Article.query.filter_by(category="studies", language=lang).all()
    media = Article.query.filter_by(category="media", language=lang).all()
    return render_template("index.html", news=news, studies=studies, media=media, lang=lang)

# ✅ API لإضافة المقالات إلى قاعدة البيانات
@app.route("/api/upload_articles", methods=["POST"])
def upload_articles():
    """استقبال وتخزين المقالات في قاعدة البيانات."""
    data = request.get_json()
    if not data or "articles" not in data:
        return jsonify({"error": "❌ البيانات غير صحيحة!"}), 400

    for article in data["articles"]:
        new_article = Article(
            title=article["title"],
            content=article["content"],
            image=article["image"],
            category=article["category"],  # تحديد القسم المناسب
            language=detect_language(article["content"])
        )
        db.session.add(new_article)

    db.session.commit()
    return jsonify({"message": "✅ تم حفظ المقالات بنجاح!"}), 201

# ✅ API لاسترجاع المقالات من قاعدة البيانات حسب القسم واللغة
@app.route("/api/get_articles/<category>/<lang>", methods=["GET"])
def get_articles(category, lang):
    """جلب المقالات المخزنة في قاعدة البيانات."""
    articles = Article.query.filter_by(category=category, language=lang).all()
    articles_list = [
        {"title": a.title, "content": a.content, "image": a.image, "category": a.category, "language": a.language}
        for a in articles
    ]
    return jsonify({"articles": articles_list})

# ✅ لوحة تحكم الأدمن (إضافة/حذف المقالات)
@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    """صفحة تسجيل الدخول إلى لوحة التحكم"""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "abo" and password == "1234":
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            return "❌ اسم المستخدم أو كلمة المرور غير صحيحة!", 403

    return render_template("admin_login.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    """لوحة تحكم الأدمن"""
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    articles = Article.query.all()
    return render_template("admin_dashboard.html", articles=articles)

# ✅ إضافة مقال جديد من لوحة التحكم
@app.route("/admin/add", methods=["POST"])
def add_article():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    new_article = Article(
        title=request.form["title"],
        content=request.form["content"],
        image=request.form["image"],
        category=request.form["category"],
        language=request.form["language"]
    )
    db.session.add(new_article)
    db.session.commit()
    return redirect(url_for("admin_dashboard"))

# ✅ حذف مقال من لوحة التحكم
@app.route("/admin/delete/<int:article_id>")
def delete_article(article_id):
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    article = Article.query.get(article_id)
    if article:
        db.session.delete(article)
        db.session.commit()
    return redirect(url_for("admin_dashboard"))

# ✅ تسجيل الخروج من لوحة التحكم
@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("home"))
@app.route('/api/publish', methods=['POST'])

def publish_article():
    data = request.json
    if "title" in data and "content" in data and "image" in data:
        df = pd.DataFrame([data])
        df.to_sql("articles", con=engine, if_exists="append", index=False)
        return jsonify({"message": "✅ تم نشر المقال بنجاح!"}), 200
    else:
        return jsonify({"error": "❌ البيانات غير مكتملة!"}), 400


# ✅ تشغيل التطبيق
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
