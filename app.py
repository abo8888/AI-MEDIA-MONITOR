@app.route('/api/upload_articles', methods=["POST"])
def api_upload_articles():
    """Receive articles from Jupyter Notebook and classify them by language."""
    
    if not request.json or "articles" not in request.json:
        return jsonify({"error": "Invalid data"}), 400

    articles = request.json["articles"]

    #  Load existing articles if available
    if os.path.exists(CSV_FILE_AR):
        df_ar = pd.read_csv(CSV_FILE_AR, encoding="utf-8-sig")
    else:
        df_ar = pd.DataFrame(columns=["title", "content", "image", "category"])

    if os.path.exists(CSV_FILE_EN):
        df_en = pd.read_csv(CSV_FILE_EN, encoding="utf-8-sig")
    else:
        df_en = pd.DataFrame(columns=["title", "content", "image", "category"])

    #  Detect language and classify articles
    new_articles_ar = []
    new_articles_en = []

    for article in articles:
        lang = detect_language(article["content"])
        if lang == "ar":
            new_articles_ar.append(article)
        else:
            new_articles_en.append(article)

    #  Append new articles and save them
    if new_articles_ar:
        df_ar = pd.concat([df_ar, pd.DataFrame(new_articles_ar)], ignore_index=True)
        df_ar.to_csv(CSV_FILE_AR, index=False, encoding="utf-8-sig")

    if new_articles_en:
        df_en = pd.concat([df_en, pd.DataFrame(new_articles_en)], ignore_index=True)
        df_en.to_csv(CSV_FILE_EN, index=False, encoding="utf-8-sig")

    return jsonify({"message": "Articles uploaded successfully!"}), 201
