# test_api.py
import requests
import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Настройки
API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL")
MODEL = "qwen2.5-32b-instruct"

# Проверка, что переменные загружены
if not API_KEY:
    print("❌ Ошибка: OPENAI_API_KEY не найден в .env")
    exit(1)
if not BASE_URL:
    print("❌ Ошибка: OPENAI_BASE_URL не найден в .env")
    exit(1)

# URL для теста
url = f"{BASE_URL}/models"

# Заголовки
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

print("🔍 Проверка доступа к API...")

# --- Тест 1: Получить список моделей ---
print("\n1. Запрос к /models...")
try:
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:
        models = response.json()
        print("✅ Успешно! Доступные модели:")
        for model in models.get("data", []):
            print(f"  - {model['id']}")
        if MODEL in [m['id'] for m in models.get("data", [])]:
            print(f"✅ Модель '{MODEL}' доступна!")
        else:
            print(f"⚠️  Модель '{MODEL}' НЕ найдена в списке.")
    else:
        print(f"❌ Ошибка: {response.status_code} — {response.text}")
except Exception as e:
    print(f"❌ Не удалось подключиться к {BASE_URL}: {str(e)}")

# --- Тест 2: Простой chat.completions запрос ---
print("\n2. Тестовый запрос к /chat/completions...")
try:
    response = requests.post(
        f"{BASE_URL}/chat/completions",
        headers=headers,
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": "Привет! Работаешь?"}],
            "max_tokens": 10
        },
        timeout=15
    )
    if response.status_code == 200:
        result = response.json()
        print("✅ Запрос выполнен успешно!")
        print("Ответ:", result["choices"][0]["message"]["content"].strip())
    elif response.status_code == 400:
        print(f"❌ 400 Bad Request: {response.text}")
        print("💡 Это может означать, что функция вызова тулзов не включена на сервере.")
    else:
        print(f"❌ Ошибка {response.status_code}: {response.text}")
except Exception as e:
    print(f"❌ Ошибка запроса: {str(e)}")