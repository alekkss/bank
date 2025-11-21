# 🤖 AI-CRM: Умная CRM-система с Open Banking интеграцией

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![AI](https://img.shields.io/badge/AI-Google%20Gemini-red.svg)

**Интеллектуальная CRM-система для финансового обслуживания клиентов с глубокой интеграцией Open Banking API и AI-ассистентом на базе Google Gemini**

[Демо](#демо) • [Возможности](#возможности) • [Установка](#установка) • [Использование](#использование) • [API](#api-документация) • [Архитектура](#архитектура)

</div>

---

## 📋 Содержание

- [О проекте](#о-проекте)
- [Возможности](#возможности)
- [Демо](#демо)
- [Технологии](#технологии)
- [Архитектура](#архитектура)
- [Установка](#установка)
- [Конфигурация](#конфигурация)
- [Использование](#использование)
- [API Документация](#api-документация)
- [Безопасность](#безопасность)
- [Deployment](#deployment)
- [Разработка](#разработка)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Лицензия](#лицензия)
- [Контакты](#контакты)

---

## 🎯 О проекте

**AI-CRM** — это современная CRM-система нового поколения, созданная специально для банков и финансовых организаций. Система автоматически подключается к банковским счетам клиентов через Open Banking API, анализирует их финансовое поведение с помощью искусственного интеллекта и предоставляет менеджерам персонализированные инсайты для улучшения обслуживания.

### Проблема, которую мы решаем

- 📊 **60% времени менеджеров** уходит на ручной сбор и анализ финансовых данных
- 🎯 Клиенты получают **нерелевантные предложения** без учёта реального поведения
- 💼 Отсутствует **единая картина клиента** при работе с несколькими банками
- 📉 **Низкая конверсия** продаж из-за отсутствия персонализации

### Наше решение

AI-CRM автоматизирует сбор данных из любых банков, анализирует финансовое поведение клиентов с помощью AI и предоставляет менеджерам готовые рекомендации для персонализированных предложений.

---

## ✨ Возможности

### 🏦 Multi-Banking интеграция
- ✅ Автоматическое подключение к счетам клиентов в любых банках
- ✅ Open Banking API (совместимо с российскими банками)
- ✅ OAuth 2.0 авторизация с consent management
- ✅ Real-time данные по транзакциям, балансам, счетам
- ✅ Поддержка 2+ банков (легко расширяется)

### 🤖 AI-ассистент
- ✅ Интеллектуальный анализ финансового поведения
- ✅ Автоматическая категоризация транзакций (12+ категорий)
- ✅ Персонализированные инсайты и рекомендации
- ✅ Google Gemini 2.5 Flash Lite (ответы за 2-3 секунды)
- ✅ Контекст до 1M токенов

### 📊 Умная аналитика
- ✅ Финансовые профили клиентов с детализацией
- ✅ Рейтинговая система клиентов (A/B/C)
- ✅ Интерактивные дашборды с метриками
- ✅ Автоматические отчёты по категориям

### 🎨 Адаптивный интерфейс
- ✅ Современный gradient-дизайн
- ✅ Responsive для всех устройств
- ✅ Real-time обновления
- ✅ Интуитивный UX

### 🔒 Безопасность
- ✅ Bcrypt хэширование паролей
- ✅ Session-based авторизация
- ✅ .env для конфиденциальных данных
- ✅ HTTP-only cookies

---

## 🎬 Демо

### Главный Dashboard
┌─────────────────────────────────────────────────────────┐
│ AI-CRM Dashboard [👤 admin] [🚪] │
├─────────────────────────────────────────────────────────┤
│ │
│ 📊 20 клиентов 💰 1,982 транзакций 🏦 2 банка │
│ │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │ team047-1 │ │ team047-2 │ │ team047-3 │ │
│ │ ⭐⭐⭐⭐⭐ │ │ ⭐⭐⭐⭐ │ │ ⭐⭐⭐ │ │
│ │ 115,038₽ │ │ 87,450₽ │ │ 45,200₽ │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ │
│ │
│ 🤖 AI Assistant │
│ ┌─────────────────────────────────────────────────┐ │
│ │ Проанализируй расходы клиента team047-1 │ │
│ │ [Send] │ │
│ └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘

text

### AI Анализ
👤 Вопрос: Проанализируй расходы клиента team047-1

🤖 AI Ответ:
На основе анализа 982 транзакций клиента team047-1 (abank):

📊 Структура расходов:

Продукты (Магнит, ВкусВилл): 15,240₽ (45%)

Рестораны (Макдоналдс, Dodopizza): 8,450₽ (25%)

Транспорт: 3,200₽ (10%)

Развлечения: 6,800₽ (20%)

💡 Рекомендации:

Высокие траты на доставку еды - предложить кредитную карту с кэшбэком

Стабильный доход (зарплата 87,894₽) - подходит для вклада на 500,000₽

Регулярные проценты по депозиту - клиент финансово грамотный

text

---

## 🛠️ Технологии

### Backend
- **Python 3.10+** - основной язык
- **Flask 3.0** - REST API фреймворк
- **SQLite** - база данных (с миграцией на PostgreSQL)
- **bcrypt** - криптографическое хэширование паролей
- **python-dotenv** - управление конфигурацией

### AI & Machine Learning
- **OpenRouter API** - доступ к AI моделям
- **Google Gemini 2.5 Flash Lite** - основная AI модель
- **Context window: 1M tokens** - огромный контекст для анализа

### Banking Integration
- **Open Banking API** - стандарт финансовых данных
- **OAuth 2.0** - безопасная авторизация
- **Consent Management** - управление согласиями клиентов

### Frontend
- **HTML5 / CSS3** - современная вёрстка
- **Vanilla JavaScript (ES6+)** - без фреймворков
- **Fetch API** - асинхронные запросы
- **CSS Grid & Flexbox** - адаптивная вёрстка

### DevOps
- **systemd** - автоматизация и мониторинг
- **Git** - контроль версий
- **VPS Ubuntu 24.04** - хостинг

---

## 🏗️ Архитектура

┌─────────────────────────────────────────────────────────────┐
│ Frontend (Browser) │
│ HTML/CSS/JavaScript │
└───────────────────────────┬─────────────────────────────────┘
│ REST API (JSON)
┌───────────────────────────▼─────────────────────────────────┐
│ Flask REST API Server │
│ ┌─────────────┐ ┌──────────────┐ ┌──────────────┐ │
│ │ app.py │ │ repositories │ │ ai_service │ │
│ │ (Routes) │──│ (Data Layer) │──│ (AI Logic) │ │
│ └─────────────┘ └──────────────┘ └──────┬───────┘ │
└───────────────────────────┬─────────────────┼───────────────┘
│ │
▼ ▼
┌─────────────────────┐ ┌─────────────────┐
│ SQLite Database │ │ OpenRouter AI │
│ (multibank_real) │ │ (Gemini 2.5) │
└─────────────────────┘ └─────────────────┘
▲
│
┌─────────────┴─────────────┐
│ base.py (Scheduler) │
│ Open Banking Data Import │
└─────────────┬─────────────┘
│
▼
┌─────────────────────────────┐
│ Open Banking APIs │
│ - Awesome Bank (abank) │
│ - Virtual Bank (vbank) │
└─────────────────────────────┘

text

### Структура проекта

ai-crm/
├── app.py # Flask REST API
├── config.py # Конфигурация
├── database.py # Database manager
├── repositories.py # Data access layer
├── ai_service.py # AI integration
├── base.py # Banking data importer
├── generate_password_hash.py # Password hashing utility
├── requirements.txt # Python dependencies
├── .env # Environment variables (НЕ в git!)
├── .gitignore # Git ignore rules
├── templates/
│ ├── index.html # Main dashboard
│ └── login.html # Login page
└── static/
├── styles.css # Styles
└── app.js # Frontend logic

text

---

## 🚀 Установка

### Требования

- Python 3.10 или выше
- pip (Python package manager)
- Git
- OpenRouter API ключ (для AI функций)
- Open Banking API credentials (CLIENT_ID, CLIENT_SECRET)

### Быстрый старт

1. **Клонируйте репозиторий**
git clone https://github.com/yourusername/ai-crm.git
cd ai-crm

text

2. **Создайте виртуальное окружение**
python3 -m venv venv
source venv/bin/activate # Linux/Mac

или
venv\Scripts\activate # Windows

text

3. **Установите зависимости**
pip install -r requirements.txt

text

4. **Создайте .env файл**
cp .env.example .env
nano .env # отредактируйте конфигурацию

text

5. **Импортируйте данные из банков**
python3 base.py

text

6. **Запустите сервер**
python3 app.py

text

7. **Откройте в браузере**
http://localhost:5000

text

**Логин:** admin  
**Пароль:** admin (измените в production!)

---

## ⚙️ Конфигурация

### Создание .env файла

Скопируйте `.env.example` в `.env` и заполните:

База данных
DATABASE_FILE=/path/to/multibank_real.db

Секретный ключ Flask (сгенерируйте случайную строку)
SECRET_KEY=your-secret-key-here

Авторизация
AUTH_USERNAME=admin
AUTH_PASSWORD_HASH=$2b$12$... # bcrypt hash

Flask настройки
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False

AI настройки
AI_API_URL=https://openrouter.ai/api/v1/chat/completions
AI_API_KEY=sk-or-v1-your-api-key
AI_MODEL=google/gemini-2.5-flash-lite
AI_MAX_TOKENS=2048
AI_TEMPERATURE=0.7
AI_TIMEOUT=30

Open Banking API
CLIENT_ID=your-client-id
CLIENT_SECRET=your-client-secret

Мок-данные для клиентов
MOCK_CONTACTS=email1@example.com:+79161234567,email2@example.com:+79162345678

text

### Генерация безопасного пароля

python3 generate_password_hash.py

text

Введите пароль, скопируйте хэш в `.env` файл.

---

## 📖 Использование

### Запуск в режиме разработки

python3 app.py

text

Сервер запустится на `http://localhost:5000`

### Импорт данных из банков

python3 base.py

text

Скрипт загрузит:
- Данные клиентов
- Счета
- Балансы
- Транзакции (автокатегоризация)
- Финансовые продукты

### Автоматическое обновление данных

Настройте systemd timer для ежедневного обновления:

sudo cp ai-crm.service /etc/systemd/system/
sudo cp ai-crm.timer /etc/systemd/system/
sudo systemctl enable ai-crm.timer
sudo systemctl start ai-crm.timer

text

Данные будут обновляться каждую ночь в 00:00.

---

## 📡 API Документация

### Аутентификация

**POST** `/api/auth/login`
{
"username": "admin",
"password": "admin"
}

text

**Response:**
{
"success": true,
"message": "Авторизация успешна"
}

text

### Клиенты

**GET** `/api/clients`  
Получить список всех клиентов

**GET** `/api/clients/:id`  
Получить детальную информацию о клиенте

**POST** `/api/clients`  
Создать нового клиента

**PUT** `/api/clients/:id`  
Обновить данные клиента

**DELETE** `/api/clients/:id`  
Удалить клиента

### AI Ассистент

**POST** `/api/ai/ask`
{
"question": "Проанализируй расходы клиента",
"client_id": "team047-1-abank"
}

text

**Response:**
{
"answer": "На основе анализа...",
"model": "google/gemini-2.5-flash-lite",
"has_context": true
}

text

**GET** `/api/ai/suggestions?client_id=team047-1-abank`  
Получить предложенные вопросы для AI

### Транзакции

**GET** `/api/clients/:id/transactions?limit=50`  
Получить транзакции клиента

**POST** `/api/transactions`  
Создать новую транзакцию (только для CRM режима)

### Статистика

**GET** `/api/stats`  
Получить общую статистику системы

{
"clients": {
"total": 20,
"active": 18,
"inactive": 2
},
"transactions": {
"count": 1982,
"income": 2500000,
"expense": 1200000,
"balance": 1300000
}
}

text

---

## 🔒 Безопасность

### Хранение паролей

Пароли хэшируются с помощью **bcrypt** (12 раундов):

import bcrypt

salt = bcrypt.gensalt(rounds=12)
hashed = bcrypt.hashpw(password.encode('utf-8'), salt)

text

### Защита API ключей

- ✅ Все секреты в `.env` файле
- ✅ `.env` добавлен в `.gitignore`
- ✅ Никогда не коммитьте секреты в git

### Session безопасность

- ✅ HTTP-only cookies
- ✅ Secure sessions
- ✅ CSRF защита (планируется)

### Best Practices

Сгенерируйте случайный SECRET_KEY
python3 -c "import secrets; print(secrets.token_hex(32))"

Используйте сильные пароли (минимум 12 символов)
Регулярно обновляйте зависимости
pip install --upgrade -r requirements.txt

text

---

## 🌐 Deployment

### Production на VPS (Ubuntu)

1. **Установите зависимости**
sudo apt update
sudo apt install python3 python3-pip python3-venv git

text

2. **Клонируйте проект**
cd /root
git clone https://github.com/yourusername/ai-crm.git
cd ai-crm

text

3. **Настройте venv**
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

text

4. **Настройте .env для production**
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

text

5. **Создайте systemd service**
sudo nano /etc/systemd/system/ai-crm.service

text
undefined
[Unit]
Description=AI-CRM Flask Application
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/ai-crm
Environment="PATH=/root/ai-crm/venv/bin"
ExecStart=/root/ai-crm/venv/bin/python3 /root/ai-crm/app.py
Restart=always

[Install]
WantedBy=multi-user.target

text

6. **Запустите сервис**
sudo systemctl daemon-reload
sudo systemctl enable ai-crm
sudo systemctl start ai-crm
sudo systemctl status ai-crm

text

7. **Настройте Nginx (опционально)**
server {
listen 80;
server_name your-domain.com;

text
location / {
    proxy_pass http://127.0.0.1:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
}

text

### Docker (в разработке)

FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python3", "app.py"]

text

---

## 👨‍💻 Разработка

### Структура кода

#### Repository Pattern

repositories.py
class ClientRepository:
@staticmethod
def get_all(status=None):
# Получить клиентов из БД
pass

text
@staticmethod
def get_by_id(client_id):
    # Получить клиента по ID
    pass
text

#### AI Service

ai_service.py
class AIService:
def build_context(self, client_id):
# Построить контекст для AI
pass

text
def ask(self, question, client_id):
    # Задать вопрос AI
    pass
text

### Добавление нового банка

1. Добавьте конфигурацию в `base.py`:
self.banks.append({
"name": "New Bank",
"code": "newbank",
"url": "https://newbank.api.com"
})

text

2. Добавьте consent ID (если требуется):
self.vbank_consents = {
"team047-1": "consent-id-here"
}

text

3. Запустите импорт:
python3 base.py

text

### Тестирование

Запустите тесты (планируется)
pytest tests/

Проверьте code style
flake8 .

Проверьте типы
mypy .

text

---

## 🗺️ Roadmap

### v1.0 (Текущая версия)
- ✅ Multi-banking интеграция (2 банка)
- ✅ AI ассистент (Google Gemini)
- ✅ Базовая CRM функциональность
- ✅ Автоматический импорт данных
- ✅ Адаптивный интерфейс

### v1.5 (Q1 2026)
- 🔄 Миграция на PostgreSQL
- 🔄 Интеграция с 10+ банками
- 🔄 Advanced AI аналитика
- 🔄 Экспорт отчётов (PDF/Excel)
- 🔄 Multi-user support

### v2.0 (Q2 2026)
- 📅 FastAPI миграция (async)
- 📅 Real-time WebSocket уведомления
- 📅 ML прогнозирование поведения
- 📅 Мобильное приложение (React Native)
- 📅 Интеграция с CRM системами

### v3.0 (Q4 2026)
- 📅 Blockchain для аудита
- 📅 Advanced security (2FA, biometrics)
- 📅 White-label решение для банков
- 📅 API marketplace

---

## 🤝 Contributing

Мы приветствуем вклад в проект! Вот как вы можете помочь:

### Как внести вклад

1. **Fork репозиторий**
2. **Создайте feature branch**
git checkout -b feature/amazing-feature

text

3. **Сделайте изменения и commit**
git commit -m "Add amazing feature"

text

4. **Push в branch**
git push origin feature/amazing-feature

text

5. **Откройте Pull Request**

### Правила

- Следуйте PEP 8 стайл-гайду
- Добавляйте docstrings для функций
- Пишите понятные commit messages
- Тестируйте код перед PR

### Отчёты об ошибках

Используйте GitHub Issues для сообщения об ошибках. Включите:
- Описание проблемы
- Шаги для воспроизведения
- Ожидаемое и фактическое поведение
- Скриншоты (если применимо)
- Версию Python и ОС

---

## 📊 Статистика проекта

- **Строк кода:** ~3,500 (Python + JavaScript)
- **Файлов:** 15
- **Commits:** 50+
- **Contributors:** 1 (пока!)
- **Поддерживаемых банков:** 2 (расширяемо)
- **AI моделей:** Google Gemini 2.5 Flash Lite
- **Время разработки MVP:** 3 дня

---

## 📄 Лицензия

Этот проект распространяется под лицензией MIT License - см. файл [LICENSE](LICENSE) для деталей.

MIT License

Copyright (c) 2025 AI-CRM Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...

text

---

## 👤 Автор

**Александр**
- Python developer специализирующийся на автоматизации бизнес-процессов с AI
- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com
- Telegram: @yourtelegram

---

## 🙏 Благодарности

- [OpenRouter](https://openrouter.ai) за доступ к Google Gemini API
- [Flask](https://flask.palletsprojects.com/) команда за отличный фреймворк
- [Open Banking](https://openbanking.org.uk/) за стандарт API
- ВТБ за проведение хакатона и вдохновение

---

## 📞 Поддержка

Если у вас возникли вопросы или проблемы:

- 📧 Email: support@ai-crm.com
- 💬 Telegram: @ai_crm_support
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/ai-crm/issues)
- 📖 Wiki: [Project Wiki](https://github.com/yourusername/ai-crm/wiki)

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/ai-crm&type=Date)](https://star-history.com/#yourusername/ai-crm&Date)

---

<div align="center">

**Сделано с ❤️ для финансового сектора**

[⬆ Наверх](#-ai-crm-умная-crm-система-с-open-banking-интеграцией)

</div>
