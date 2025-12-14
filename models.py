from sqlalchemy import Column, Integer, Boolean, String, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()

MODELS = {
    "llama": {
        "id": "meta-llama/llama-3.3-70b-instruct:free",
        "title": "LLaMA"
    },
    "gpt": {
        "id": "openai/gpt-oss-20b:free",
        "title": "GPT"
    }
}

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    paid = Column(Boolean, default=False)
    current_model = Column(String, default="meta-llama/llama-3.3-70b-instruct:free")
    history = Column(JSON, default=lambda: {})
