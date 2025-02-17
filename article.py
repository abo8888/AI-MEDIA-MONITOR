from flask_sqlalchemy import SQLAlchemy
from langdetect import detect

db = SQLAlchemy()

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    # باقي الأعمدة ...



    def __init__(self, title, content, image=None, category="news"):
        self.title = title.strip()
        self.content = content.strip()
        self.image = image.strip() if image else None
        self.category = category.strip()
        self.language = self.detect_language(content)

    @staticmethod
    def detect_language(text):
        """تحليل اللغة تلقائيًا عند إنشاء المقال"""
        try:
            lang = detect(text)
            return lang if lang in ["ar", "en", "de"] else "en"
        except Exception as e:
            print(f"⚠️ خطأ في كشف اللغة: {e}")
            return "unknown"

    def to_dict(self):
        """تحويل المقال إلى JSON للاستجابة API"""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "image": self.image if self.image else "https://via.placeholder.com/300",
            "category": self.category.capitalize(),
            "language": self.language
        }
