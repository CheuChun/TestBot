import aiohttp
import os
from dotenv import load_dotenv
from logging_config import logger

load_dotenv()
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = os.getenv("OPENROUTER_API_KEY")

async def call_openrouter(messages):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "nex-agi/deepseek-v3.1-nex-n1:free",
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
                content = data["choices"][0]["message"]["content"]
                return content
        except Exception as e:
            logger.exception(f"Ошибка при вызове OpenRouter: {e}")
            return "Ошибка при обработке запроса ИИ"
