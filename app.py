from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import os

# ✅ إعداد Flask
app = Flask(__name__)

# ✅ تحديد مسار الملفات المخزنة
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
CSV_FILE = os.path.join(UPLOAD_FOLDER, "articles.csv")

# ✅ بيانات تسجيل الدخول للمشرف (يمكنك تخصيصها)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"  # ⚠️ قم بتغييرها إلى كلمة مرور قوية

# ✅ تحميل المقالات من CSV
def load_articles():
    """ تحميل المقالات من ملف CSV """
    if not os.path.exists(CSV_FILE):
        return []
    
    df = pd.read_csv(CSV_FILE, encoding="utf-8-sig")

    # ✅ التأكد من صحة الأعمدة
    required_columns = {"title", "content", "image", "category"}
    if not required_columns.issubset(df.columns):
        print(f"🚨 الأعمدة المفقودة: {required_columns - set(df.columns)}")
        return []
    
    return df.to_dict(orient="records")

# ✅ صفحة تسجيل الدخول
@app.route('/admin/login', methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            return redirect(url_for("admin_dashboard"))
        else:
            return "🚨 خطأ في تسجيل الدخول، تأكد من البيانات!", 403

    return render_template("admin_login.html")

# ✅ لوحة تحكم المشرف
@app.route('/admin/dashboard')
def admin_dashboard():
    articles = load_articles()
    return render_template("admin_dashboard.html", articles=articles)

# ✅ إضافة مقال جديد عبر لوحة التحكم
@app.route('/admin/add_article', methods=["POST"])
def add_article():
    """ إضافة مقال جديد إلى الموقع """
    data = {
        "title": request.form["title"],
        "content": request.form["content"],
        "image": request.form["image"],
        "category": request.form["category"]
    }

    # ✅ تحميل المقالات القديمة
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE, encoding="utf-8-sig")
    else:
        df = pd.DataFrame(columns=["title", "content", "image", "category"])

    # ✅ إضافة المقال الجديد
    df = df.append(data, ignore_index=True)
    df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")

    return redirect(url_for("admin_dashboard"))

# ✅ حذف مقال
@app.route('/admin/delete_article/<int:article_id>')
def delete_article(article_id):
    """ حذف مقال من القائمة """
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE, encoding="utf-8-sig")
        df = df.drop(article_id, axis=0).reset_index(drop=True)
        df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")

    return redirect(url_for("admin_dashboard"))

# ✅ تشغيل التطبيق
if __name__ == '__main__':
    app.run(debug=True)
