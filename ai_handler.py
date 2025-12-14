import aiohttp
import os
from dotenv import load_dotenv
from logging_config import logger

load_dotenv()
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = os.getenv("OPENROUTER_API_KEY")


async def call_openrouter(messages, model: str):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": messages
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(OPENROUTER_URL, json=payload, headers=headers) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    logger.error(f"OpenRouter API returned {resp.status}: {text}")
                    return "Ошибка при обращении к ИИ"

                data = await resp.json()
                choices = data.get("choices")
                if not choices or "message" not in choices[0] or "content" not in choices[0]["message"]:
                    logger.error(f"Неправильный формат ответа OpenRouter: {data}")
                    return "Ошибка в ответе ИИ"

                content = choices[0]["message"]["content"]
                return content
        except Exception as e:
            logger.exception(f"Ошибка при вызове OpenRouter: {e}")
            return "Ошибка при обработке запроса ИИ"
