from flask_sqlalchemy import SQLAlchemy
from langdetect import detect, DetectorFactory
from datetime import datetime
import textwrap

db = SQLAlchemy()
DetectorFactory.seed = 42  # لضمان تكرار نتائج الكشف عن اللغة

class Article(db.Model):
    """Article model for storing news articles."""
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier
    title = db.Column(db.String(255), nullable=False)  # Article title
    content = db.Column(db.Text, nullable=False)  # Full content
    image = db.Column(db.String(255), nullable=True)  # Image URL
    category = db.Column(db.String(50), nullable=False, default="news")  # Category
    language = db.Column(db.String(10), nullable=False, default="en")  # Language
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Creation timestamp
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Last update timestamp

    def __init__(self, title, content, image=None, category="news"):
        """Initialize an article with automatic language detection."""
        self.title = title.strip()
        self.content = content.strip()
        self.image = image.strip() if image else None
        self.category = category.strip().lower()  # جعل الفئة بصيغة موحدة
        self.language = self.detect_language(f"{title} {content}")

    @staticmethod
    def detect_language(text):
        """Detect the language of the article using langdetect."""
        try:
            if text and len(text) > 20:  # تأكيد أن النص ليس قصيرًا جدًا
                lang = detect(text)
                return lang if lang in ["ar", "en", "de"] else "en"
            return "unknown"
        except Exception as e:
            print(f"⚠️ Language detection error: {e}")
            return "unknown"

    def to_dict(self):
        """Convert the article to a dictionary for JSON responses."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.get_short_content(),
            "image": self.image if self.image else "https://via.placeholder.com/300",
            "category": self.category.capitalize(),
            "language": self.language,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None
        }

    def get_short_content(self, max_length=200):
        """Shorten content while preventing word breaks."""
        if len(self.content) <= max_length:
            return self.content
        return textwrap.shorten(self.content, width=max_length, placeholder="...")

    def __repr__(self):
        """Return a string representation of the article."""
        return f"<Article {self.id}: {self.title[:30]}... ({self.language})>"
