# Async Review Sentiment API

Асинхронный HTTP-сервис на FastAPI, который принимает отзывы пользователей, определяет их настроение (positive, negative или neutral) и сохраняет в базу данных SQLite. Есть возможность фильтрации отзывов по тональности.

## Установка и запуск

```bash
pip install fastapi uvicorn aiosqlite
uvicorn main:app --reload
```

## Примеры запросов

### Добавление отзыва

**POST** `/reviews`

**Тело запроса:**
```json
{
  "text": "Обожаю ваш сервис!"
}
```

**Ответ:**
```json
{
  "id": 1,
  "text": "Обожаю ваш сервис!",
  "sentiment": "positive",
  "created_at": "2025-07-17T12:35:22Z"
}
```

### Получение всех отзывов

**GET** `/reviews`

**Ответ:**
```json
[
  {
    "id": 1,
    "text": "Обожаю ваш сервис!",
    "sentiment": "positive",
    "created_at": "2025-07-17T12:35:22Z"
  },
  {
    "id": 2,
    "text": "Это отстой!",
    "sentiment": "negative",
    "created_at": "2025-07-17T12:36:12Z"
  }
]
```

### Получение только негативных отзывов

**GET** `/reviews?sentiment=negative`

**Ответ:**
```json
[
  {
    "id": 2,
    "text": "Это отстой!",
    "sentiment": "negative",
    "created_at": "2025-07-17T12:36:12Z"
  }
]
```

### Получение только нейтральных отзывов

**GET** `/reviews?sentiment=neutral`

**Ответ:**
```json
[
  {
    "id": 3,
    "text": "Просто оставляю отзыв",
    "sentiment": "neutral",
    "created_at": "2025-07-17T12:37:15Z"
  }
]
```

### Некорректное значение sentiment

**GET** `/reviews?sentiment=bad`

**Ответ:**
```json
{
  "detail": "Unsupported sentiment value"
}
```

## Примеры curl-запросов

### Добавление отзыва
```bash
curl -X POST "http://localhost:8000/reviews" \
     -H "Content-Type: application/json" \
     -d '{"text": "Обожаю ваш сервис!"}'
```

### Получение всех отзывов
```bash
curl -X GET "http://localhost:8000/reviews"
```

### Получение негативных отзывов
```bash
curl -X GET "http://localhost:8000/reviews?sentiment=negative"
```

### Получение позитивных отзывов
```bash
curl -X GET "http://localhost:8000/reviews?sentiment=positive"
```

### Получение нейтральных отзывов
```bash
curl -X GET "http://localhost:8000/reviews?sentiment=neutral"
```