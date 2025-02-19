from flask_sqlalchemy import SQLAlchemy
from langdetect import detect, DetectorFactory
from datetime import datetime

db = SQLAlchemy()
DetectorFactory.seed = 42  # لضمان تكرار نتائج الكشف عن اللغة

class Article(db.Model):
    """Article model for storing news articles."""
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier
    title = db.Column(db.String(255), nullable=False)  # Article title
    content = db.Column(db.UnicodeText, nullable=False)  # Full content (supports large text)
    image = db.Column(db.String(255), nullable=True)  # Image URL
    category = db.Column(db.String(50), nullable=False, default="news")  # Category
    language = db.Column(db.String(10), nullable=False, default="en")  # Language
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Creation timestamp
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Last update timestamp

    def __init__(self, title, content, image=None, category="news"):
        """Initialize an article with automatic language detection."""
        self.title = title.strip() if title else "Untitled"
        self.content = content.strip() if content else "No content available"
        self.image = image.strip() if image else None
        self.category = category.strip().lower() if category else "news"
        self.language = self.detect_language(f"{title} {content}")

    @staticmethod
    def detect_language(text):
        """Detect the language of the article using langdetect."""
        try:
            if text and len(text) > 10:  # تقليل الحد الأدنى للنص
                lang = detect(text)
                return lang if lang in ["ar", "en", "de"] else "en"
            return "en"  # جعل اللغة الافتراضية "en"
        except Exception as e:
            print(f"⚠️ Language detection error: {e}")
            return "en"

    def to_dict(self):
        """Convert the article to a dictionary for JSON responses."""
        return {
            "id": self.id,
            "title": self.title or "Untitled",
            "content": self.get_short_content(),
            "image": self.image or "https://via.placeholder.com/300",
            "category": self.category.capitalize() if self.category else "General",
            "language": self.language or "en",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "Unknown",
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else "Unknown"
        }

    def get_short_content(self, max_length=200):
        """Shorten content while preventing word breaks."""
        if len(self.content) <= max_length:
            return self.content
        return self.content[:max_length].rsplit(' ', 1)[0] + "..."

    def __repr__(self):
        """Return a string representation of the article."""
        return f"<Article {self.id}: {self.title[:30]}... ({self.language})>"
