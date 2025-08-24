# tests/test_api.py
import os
import pytest
import requests
from dotenv import load_dotenv
from pathlib import Path

# Пытаемся загрузить .env только если файл существует
env_path = Path('.env')
if env_path.exists():
    load_dotenv()
else:
    API_KEY = None
    BASE_URL = None

# Получаем значения из переменных окружения
API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL")
MODEL = os.getenv("OPENAI_MODEL")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}" if API_KEY else "",
    "Content-Type": "application/json",
}


@pytest.fixture(autouse=True)
def check_env():
    """Проверка наличия ключа и URL перед тестами API"""
    if not env_path.exists():
        pytest.skip("❌ Файл .env не найден")
    if not API_KEY or not BASE_URL:
        pytest.skip("❌ Переменные окружения OPENAI_API_KEY / OPENAI_BASE_URL не заданы")


def test_list_models():
    """Проверяем, что API возвращает список моделей"""
    url = f"{BASE_URL}/models"
    response = requests.get(url, headers=HEADERS, timeout=10)

    assert response.status_code == 200, f"Ошибка {response.status_code}: {response.text}"

    data = response.json()
    assert "data" in data, "Ответ API не содержит ключ 'data'"

    models = [m["id"] for m in data["data"]]
    assert models, "Список моделей пуст"
    assert MODEL in models, f"Модель '{MODEL}' не найдена в списке"


def test_chat_completion():
    """Проверяем базовый запрос к /chat/completions"""
    url = f"{BASE_URL}/chat/completions"
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": "Привет! Работаешь?"}],
        "max_tokens": 10,
    }

    response = requests.post(url, headers=HEADERS, json=payload, timeout=15)
    assert response.status_code == 200, f"Ошибка {response.status_code}: {response.text}"

    result = response.json()
    assert "choices" in result, "Нет поля 'choices' в ответе"
    assert result["choices"][0]["message"]["content"], "Ответ пустой"
