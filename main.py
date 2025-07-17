# main.py
import re
import aiosqlite
from datetime import datetime
from fastapi import FastAPI, Depends, Query, HTTPException
from pydantic import BaseModel
from typing import Optional, List

DB_PATH = "reviews.db"
ALLOWED_SENTIMENTS = {"positive", "neutral", "negative"}

app = FastAPI(title="Async Review Sentiment API")

# ---------- Предкомпилированные Regex-паттерны ----------
POSITIVE_PATTERNS = [
    re.compile(r"\bхорош\w*\b", re.IGNORECASE),
    re.compile(r"\bлюбл\w*\b", re.IGNORECASE),
    re.compile(r"\bобожа\w*\b", re.IGNORECASE),
    re.compile(r"\bотличн\w*\b", re.IGNORECASE),
    re.compile(r"\bнрав(?:ит|ится)?\b", re.IGNORECASE),
    re.compile(r"\bсупер\b", re.IGNORECASE),
    re.compile(r"\bкласс\w*\b", re.IGNORECASE),
]

NEGATIVE_PATTERNS = [
    re.compile(r"\bплох\w*\b", re.IGNORECASE),
    re.compile(r"\bненавиж\w*\b", re.IGNORECASE),
    re.compile(r"\bужас\w*\b", re.IGNORECASE),
    re.compile(r"\bотстой\b", re.IGNORECASE),
    re.compile(r"\bужасн\w*\b", re.IGNORECASE),
    re.compile(r"\bотвратительн\w*\b", re.IGNORECASE),
]

# ---------- Pydantic модели ----------
class ReviewIn(BaseModel):
    text: str

class ReviewOut(BaseModel):
    id: int
    text: str
    sentiment: str
    created_at: str

# ---------- Функция анализа тональности ----------
def get_sentiment(text: str) -> str:
    for pattern in POSITIVE_PATTERNS:
        if pattern.search(text):
            return "positive"
    for pattern in NEGATIVE_PATTERNS:
        if pattern.search(text):
            return "negative"
    return "neutral"

# ---------- Инициализация базы данных ----------
@app.on_event("startup")
async def startup():
    async with aiosqlite.connect(DB_PATH, timeout=10) as db:
        await db.execute("PRAGMA journal_mode=WAL;")
        await db.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                sentiment TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        await db.commit()

# ---------- Зависимость для получения подключения к БД ----------
async def get_db():
    db = await aiosqlite.connect(DB_PATH, timeout=10)
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()

# ---------- POST /reviews ----------
@app.post("/reviews", response_model=ReviewOut)
async def create_review(review: ReviewIn, db=Depends(get_db)):
    sentiment = get_sentiment(review.text)
    created_at = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    cursor = await db.execute(
        "INSERT INTO reviews (text, sentiment, created_at) VALUES (?, ?, ?)",
        (review.text, sentiment, created_at)
    )
    await db.commit()
    review_id = cursor.lastrowid

    return ReviewOut(
        id=review_id,
        text=review.text,
        sentiment=sentiment,
        created_at=created_at
    )

# ---------- GET /reviews ----------
@app.get("/reviews", response_model=List[ReviewOut])
async def get_reviews(
    sentiment: Optional[str] = Query(default=None),
    db=Depends(get_db)
):
    if sentiment and sentiment not in ALLOWED_SENTIMENTS:
        raise HTTPException(status_code=422, detail="Unsupported sentiment value")

    if sentiment:
        query = """
            SELECT * FROM reviews
            WHERE sentiment = ?
            ORDER BY created_at DESC
        """
        cursor = await db.execute(query, (sentiment,))
    else:
        query = "SELECT * FROM reviews ORDER BY created_at DESC"
        cursor = await db.execute(query)

    rows = await cursor.fetchall()
    return [ReviewOut(**dict(row)) for row in rows]