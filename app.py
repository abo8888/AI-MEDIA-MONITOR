from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
from dotenv import load_dotenv
from datetime import datetime

# ✅ تحميل المتغيرات البيئية
load_dotenv()

# ✅ إعداد Flask
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "123456")

# ✅ تكوين قاعدة البيانات
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "postgresql://ai_news_db_user:4dddE4EkwvJMycr2BVgAezLaOQVnxbKb@dpg-cumvu81u0jms73b97nc0-a:5432/database")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# ✅ استيراد النماذج
from article import Article, Section, Page, Settings

# ✅ إنشاء الجداول إذا لم تكن موجودة
with app.app_context():
    db.create_all()

# ✅ صفحة تسجيل الدخول للمشرف
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == "abo" and password == "1234":
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            return "❌ خطأ في تسجيل الدخول!", 403
    return render_template("admin_login.html")

# ✅ لوحة التحكم
@app.route("/admin")
def admin_dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    
    articles = Article.query.all()
    sections = Section.query.all()
    pages = Page.query.all()
    return render_template("admin_dashboard.html", articles=articles, sections=sections, pages=pages)

# ✅ API لإضافة مقالة جديدة
@app.route("/admin/add_article", methods=["POST"])
def add_article():
    if not session.get("admin"):
        return jsonify({"error": "غير مصرح لك!"}), 403
    
    data = request.json
    new_article = Article(
        title=data["title"],
        content=data["content"],
        image=data["image"],
        category=data["category"],
        language=data["language"]
    )
    db.session.add(new_article)
    db.session.commit()
    return jsonify({"message": "✅ تمت إضافة المقالة بنجاح!"}), 201

# ✅ API لحذف المقالات
@app.route("/admin/delete_article/<int:id>", methods=["DELETE"])
def delete_article(id):
    if not session.get("admin"):
        return jsonify({"error": "غير مصرح لك!"}), 403
    
    article = Article.query.get(id)
    if article:
        db.session.delete(article)
        db.session.commit()
        return jsonify({"message": "🗑️ تم حذف المقالة!"})
    return jsonify({"error": "❌ المقالة غير موجودة!"}), 404

# ✅ API لإضافة صفحة جديدة
@app.route("/admin/add_page", methods=["POST"])
def add_page():
    if not session.get("admin"):
        return jsonify({"error": "غير مصرح لك!"}), 403

    data = request.json
    new_page = Page(
        title=data["title"],
        content=data["content"],
        slug=data["slug"]
    )
    db.session.add(new_page)
    db.session.commit()
    return jsonify({"message": "✅ تمت إضافة الصفحة!"}), 201

# ✅ تشغيل التطبيق
if __name__ == "__main__":
    app.run(debug=True)
