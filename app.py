from flask import Flask, request, jsonify
import pandas as pd
import os

# ✅ Initialize Flask App
app = Flask(__name__)

# ✅ Define Upload Paths for Arabic and English Articles
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
CSV_FILE_AR = os.path.join(UPLOAD_FOLDER, "articles_ar.csv")
CSV_FILE_EN = os.path.join(UPLOAD_FOLDER, "articles_en.csv")

# ✅ API Endpoint to Receive Arabic & English Article Files
@app.route('/api/upload_articles', methods=["POST"])
def upload_articles():
    """ API to Upload Arabic and English CSV Files """
    
    # ✅ Check if files are included in the request
    if "file_ar" not in request.files or "file_en" not in request.files:
        return jsonify({"error": "Both Arabic and English files are required!"}), 400

    file_ar = request.files["file_ar"]
    file_en = request.files["file_en"]

    # ✅ Save the Arabic CSV file
    if file_ar.filename.endswith(".csv"):
        file_ar.save(CSV_FILE_AR)
    
    # ✅ Save the English CSV file
    if file_en.filename.endswith(".csv"):
        file_en.save(CSV_FILE_EN)

    return jsonify({"message": "Files uploaded successfully!"}), 201

# ✅ Function to Load Arabic and English Articles
def load_articles():
    """ Load Arabic and English articles separately """
    articles = {"ar": [], "en": []}
    
    if os.path.exists(CSV_FILE_AR):
        df_ar = pd.read_csv(CSV_FILE_AR, encoding="utf-8-sig")
        if {"title", "article", "image_url", "category"}.issubset(df_ar.columns):
            df_ar = df_ar.rename(columns={"article": "content", "image_url": "image"})
            articles["ar"] = df_ar.to_dict(orient="records")

    if os.path.exists(CSV_FILE_EN):
        df_en = pd.read_csv(CSV_FILE_EN, encoding="utf-8-sig")
        if {"title", "article", "image_url", "category"}.issubset(df_en.columns):
            df_en = df_en.rename(columns={"article": "content", "image_url": "image"})
            articles["en"] = df_en.to_dict(orient="records")
    
    return articles

# ✅ Home Route to Display Articles
@app.route('/')
def home():
    articles = load_articles()
    return render_template("index.html", news_ar=articles["ar"], news_en=articles["en"])

# ✅ Run Flask App
if __name__ == '__main__':
    app.run(debug=True)
