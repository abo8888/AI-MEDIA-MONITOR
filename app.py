import os
import pandas as pd
from flask import Flask, render_template, request, jsonify
from langdetect import detect

# ✅ Initialize Flask App
app = Flask(__name__)

# ✅ Define Upload Path for Articles
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
CSV_FILE = os.path.join(UPLOAD_FOLDER, "articles.csv")

# ✅ Function to Detect Language
def detect_language(text):
    try:
        lang = detect(text)
        return "ar" if lang == "ar" else "en"
    except:
        return "unknown"

# ✅ Function to Load Articles from CSV
def load_articles():
    """ Load articles and categorize them by language. """
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

# ✅ API Endpoint to Receive Articles from Your Project
@app.route('/api/add_article', methods=["POST"])
def add_article():
    """ API to Receive New Articles from Your Project """
    data = request.json  # Get JSON Data
    if not data:
        return jsonify({"error": "Invalid request, no data received"}), 400
    
    required_fields = {"title", "content", "image", "category"}
    if not required_fields.issubset(data.keys()):
        return jsonify({"error": "Missing required fields"}), 400

    # ✅ Load Existing Articles
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE, encoding="utf-8-sig")
    else:
        df = pd.DataFrame(columns=["title", "content", "image", "category", "language"])

    # ✅ Detect Article Language
    data["language"] = detect_language(data["content"])

    # ✅ Append New Article
    df = df.append(data, ignore_index=True)

    # ✅ Save Updated Articles
    df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")

    return jsonify({"message": "Article added successfully"}), 201

# ✅ Home Route - Display Articles
@app.route('/')
def home():
    articles = load_articles()
    return render_template("index.html", news_ar=articles["ar"], news_en=articles["en"])

# ✅ Run Flask App
if __name__ == '__main__':
    app.run(debug=True)


# ✅ Load images from a folder
def load_images():
    images_folder = "static/images/"
    return [f"/{images_folder}{img}" for img in os.listdir(images_folder) if img.endswith((".png", ".jpg", ".jpeg"))]

# ✅ Modify home route to send images to index.html
@app.route('/')
def home():
    articles = load_articles()
    images = load_images()  # Get images from the static folder
    return render_template("index.html", news_ar=articles["ar"], news_en=articles["en"], images=images)

