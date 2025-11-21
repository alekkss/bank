import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # База данных
    DATABASE_FILE = os.getenv('DATABASE_FILE', 'root/ai-crm/multibank_real.db')
    
    # Flask настройки
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    # Секретный ключ Flask
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24).hex())
    
    # Авторизация
    AUTH_USERNAME = os.getenv('AUTH_USERNAME', 'admin')
    AUTH_PASSWORD_HASH = os.getenv('AUTH_PASSWORD_HASH', '')
    
    # Настройки AI
    AI_API_URL = os.getenv('AI_API_URL', 'https://openrouter.ai/api/v1/chat/completions')
    AI_API_KEY = os.getenv('AI_API_KEY', '')
    AI_MODEL = os.getenv('AI_MODEL', 'google/gemini-2.5-flash-lite')
    AI_MAX_TOKENS = int(os.getenv('AI_MAX_TOKENS', 2048))
    AI_TEMPERATURE = float(os.getenv('AI_TEMPERATURE', 0.7))
    AI_TIMEOUT = int(os.getenv('AI_TIMEOUT', 30))
    
    # Мок-контакты для клиентов (парсинг из .env)
    @staticmethod
    def get_mock_contacts():
        """
        Парсит контакты из .env в формате email:phone,email:phone
        Возвращает список кортежей [(email, phone), ...]
        """
        contacts_str = os.getenv('MOCK_CONTACTS', '')
        if not contacts_str:
            return []
        
        contacts = []
        for contact in contacts_str.split(','):
            contact = contact.strip()
            if ':' in contact:
                email, phone = contact.split(':', 1)
                contacts.append((email.strip(), phone.strip()))
        
        return contacts
    
    # Промпт для AI системы
    AI_SYSTEM_PROMPT = """
Ты — AI-консультант в CRM-системе для финансового анализа. 
Твоя задача — помогать менеджерам анализировать клиентов и их транзакции.

Правила работы:
1. Отвечай на русском языке простым и понятным языком
2. Используй предоставленный контекст о клиенте для точных ответов
3. Если данных недостаточно — так и скажи, не придумывай!
4. Для сумм используй формат: 125,000 ₽
5. Давай конкретные рекомендации на основе данных
6. Будь вежливым и профессиональным
7. Если видишь проблемы (например, большой минус) — предупреди менеджера
"""
    
    # Категории транзакций
    TRANSACTION_CATEGORIES = [
        "Зарплата", "Продажи", "Инвестиции", "Другие доходы",
        "Аренда", "Продукты", "Транспорт", "Развлечения",
        "Коммунальные услуги", "Здоровье", "Образование", "Одежда",
        "Связь", "Другие расходы"
    ]
    
    # Статусы клиентов
    CLIENT_STATUSES = {
        'active': 'Активен',
        'inactive': 'Неактивен',
        'vip': 'VIP',
        'blocked': 'Заблокирован'
    }
