import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from langdetect import detect

# ✅ Initialize Flask App
app = Flask(__name__)

# ✅ Configure Upload Folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
CSV_FILE = os.path.join(UPLOAD_FOLDER, "articles.csv")

# ✅ Function to Detect Language of a Given Text
def detect_language(text):
    try:
        lang = detect(text)
        return "ar" if lang == "ar" else "en"
    except:
        return "unknown"

# ✅ Function to Load and Categorize Articles by Language
def load_articles():
    """ Load articles from CSV and classify them into Arabic and English. """
    if not os.path.exists(CSV_FILE):
        return {"ar": [], "en": []}
    
    try:
        df = pd.read_csv(CSV_FILE, encoding="utf-8-sig")

        # ✅ Ensure Required Columns Exist
        required_columns = {"title", "article", "image_url", "category"}
        if not required_columns.issubset(df.columns):
            print(f"🚨 Missing columns: {required_columns - set(df.columns)}")
            return {"ar": [], "en": []}

        df = df.rename(columns={"article": "content", "image_url": "image"})
        
        # ✅ Detect Language for Each Article
        df["language"] = df["content"].apply(detect_language)
        
        # ✅ Separate Arabic and English Articles
        articles_ar = df[df["language"] == "ar"].to_dict(orient="records")
        articles_en = df[df["language"] == "en"].to_dict(orient="records")
        
        return {"ar": articles_ar, "en": articles_en}
    
    except Exception as e:
        print(f"🚨 Error loading articles: {e}")
        return {"ar": [], "en": []}

# ✅ Home Route - Display Articles by Language
@app.route('/')
def home():
    articles = load_articles()
    return render_template("index.html", news_ar=articles["ar"], news_en=articles["en"])

# ✅ Upload Route - Handle CSV File Upload
@app.route('/upload', methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            return "🚨 No file uploaded!", 400

        file = request.files["file"]
        if file.filename == "":
            return "🚨 No file selected!", 400

        if file and file.filename.endswith(".csv"):
            filename = secure_filename("articles.csv")  # Save the file with a fixed name
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            return redirect(url_for("home"))

    return '''
    <!doctype html>
    <html lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>Upload CSV File</title>
    </head>
    <body>
        <h1>📤 Upload New CSV File</h1>
        <form action="" method="post" enctype="multipart/form-data">
            <input type="file" name="file">
            <input type="submit" value="Upload File">
        </form>
    </body>
    </html>
    '''

# ✅ Run Flask App
if __name__ == '__main__':
    app.run(debug=True)
