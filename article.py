from flask_sqlalchemy import SQLAlchemy
from langdetect import detect

db = SQLAlchemy()

# ✅ نموذج المقال في قاعدة البيانات
class Article(db.Model):
    __tablename__ = "articles"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255))
    category = db.Column(db.String(100), nullable=False)
    language = db.Column(db.String(10), nullable=False)

    def __init__(self, title, content, image, category):
        self.title = title
        self.content = content
        self.image = image
        self.category = category
        self.language = self.detect_language(content)

    def detect_language(self, text):
        """تحليل اللغة تلقائيًا عند إنشاء المقال"""
        try:
            lang = detect(text)
            return "ar" if lang == "ar" else "en"
        except:
            return "unknown"

    def to_dict(self):
        """تحويل المقال إلى JSON للاستجابة API"""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "image": self.image,
            "category": self.category,
            "language": self.language
        }