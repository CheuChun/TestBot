# TestBot

---

## Выполнено

- Интеграция с ИИ через OpenRouter с помощью `aiohttp` (уровень 0),
- Сохранение в памяти 5 последних сообщений (уровень 0),
- Добавлена оплата доступа к боту через Telegram Stars (уровень 1).

---

## Установка

1. Клонируйте репозиторий:

```bash
git clone <URL_REPO>
cd TestBot
```

2. Установите зависимости:

Если не установлено `uv`

```bash
pip install uv
```

Затем

```bash
uv pip install -r requirements.txt
```

3. Создайте файл `.env` в корне проекта:

```
BOT_TOKEN=ваш_токен_Telegram
OPENROUTER_API_KEY=ваш_API_ключ_OpenRouter
```
> Токены и ключ запросить в лс
