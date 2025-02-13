import os
import pandas as pd
from flask import Flask, render_template

# ✅ تعريف `Flask` أولاً
app = Flask(__name__)

# ✅ تحديد مسار الملف الصحيح
FILE_PATH = r"C:\Users\aboro\Documents\AI\F P\articles_with_pexels_images (3).csv"

# 📰 وظيفة تحميل المقالات من CSV
def load_articles():
    """ تحميل المقالات والتأكد من أن جميع الأعمدة صحيحة. """
    if not os.path.exists(FILE_PATH):
        print("❌ ملف المقالات غير موجود! تأكد من المسار الصحيح.")
        return []

    try:
        # ✅ قراءة الملف مع التأكد من الترميز الصحيح
        df = pd.read_csv(FILE_PATH, encoding="utf-8-sig")

        # ✅ عرض الأعمدة المتاحة لمساعدتنا في التصحيح
        print("📌 الأعمدة المتاحة في CSV:", df.columns)

        # ✅ التأكد من أن الأعمدة المطلوبة موجودة
        required_columns = {"title", "article", "image_url"}
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            print(f"🚨 الأعمدة المفقودة: {missing_columns}")
            return []

        # ✅ إعادة تسمية الأعمدة لتتوافق مع `index.html`
        df = df.rename(columns={"article": "content", "image_url": "image"})

        # ✅ إضافة عمود `category` إذا لم يكن موجودًا
        if "category" not in df.columns:
            df["category"] = "غير مصنف"

        return df.to_dict(orient="records")  # تحويل البيانات إلى قائمة من القواميس
    except Exception as e:
        print(f"🚨 خطأ أثناء تحميل المقالات: {e}")
        return []

# ✅ تعريف مسار الصفحة الرئيسية
@app.route('/')
def home():
    news = load_articles()  # تحميل المقالات من CSV
    categories = list(set(article["category"] for article in news if "category" in article))
    return render_template("index.html", news=news, categories=categories)

# ✅ تعريف مسار صفحة تفاصيل المقال
@app.route('/news/<int:news_id>')
def news_details(news_id):
    news = load_articles()
    if 0 <= news_id < len(news):
        return render_template("news_details.html", article=news[news_id])
    else:
        return "<h1>🚨 المقال غير موجود!</h1>", 404

# ✅ تشغيل التطبيق
if __name__ == '__main__':
    app.run(debug=True)
