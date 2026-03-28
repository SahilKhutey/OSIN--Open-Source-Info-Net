import torch
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from app.config import settings

class NLPEngine:
    def __init__(self):
        # Using a lightweight, effective embedding model as per blueprint
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    def get_embeddings(self, text: str):
        return self.embedding_model.encode(text).tolist()

    def summarize(self, text: str, max_length: int = 130, min_length: int = 30):
        if len(text) < 100:
            return text
        result = self.summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
        return result[0]['summary_text']

nlp_engine = NLPEngine()
