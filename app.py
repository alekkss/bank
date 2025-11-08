# app.py
"""
Flask REST API для AI CRM системы
Endpoints для работы с клиентами, транзакциями и AI
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Optional

from config import Config
from repositories import (
    ClientRepository,
    TransactionRepository,
    AIConversationRepository
)
from ai_service import ai_service


app = Flask(__name__)
CORS(app)  # Разрешаем кросс-доменные запросы


# ============ CLIENTS ENDPOINTS ============

@app.route('/api/clients', methods=['GET'])
def get_clients():
    """Получить список всех клиентов"""
    try:
        print("📥 Запрос списка клиентов")
        status = request.args.get('status')
        print(f"🔍 Фильтр статуса: {status}")
        
        clients = ClientRepository.get_all(status=status)
        print(f"✅ Загружено клиентов: {len(clients)}")
        print(f"📊 Первые 3 клиента: {clients[:3] if clients else 'Нет данных'}")
        
        return jsonify({'clients': clients}), 200
    except Exception as e:
        print(f"❌ ОШИБКА в get_clients: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/clients/<client_id>', methods=['GET'])
def get_client_details(client_id):
    """Получить детальную информацию о клиенте"""
    try:
        print(f"🔍 Запрос клиента: {client_id}")
        
        # Получаем данные клиента
        client = ClientRepository.get_by_id(client_id)
        if not client:
            print(f"❌ Клиент не найден: {client_id}")
            return jsonify({'error': 'Клиент не найден'}), 404
        
        print(f"✅ Найден клиент: {client}")
        
        # Получаем транзакции
        transactions = TransactionRepository.get_by_client(client_id)
        print(f"📊 Транзакций: {len(transactions)}")
        
        # Получаем финансовую сводку
        summary = TransactionRepository.get_summary(client_id)
        print(f"💰 Сводка: {summary}")
        
        # Получаем историю AI диалогов
        conversations = AIConversationRepository.get_by_client(client_id, limit=10)
        
        # Получаем статистику по категориям
        categories = TransactionRepository.get_by_category(client_id)
        
        return jsonify({
            'client': client,
            'transactions': transactions,
            'summary': summary,
            'conversations': conversations,
            'categories': categories
        }), 200
        
    except Exception as e:
        print(f"❌ Ошибка получения клиента: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/clients', methods=['POST'])
def create_client():
    """Создать нового клиента"""
    try:
        data = request.json
        
        # Валидация
        if not data.get('name'):
            return jsonify({'error': 'Имя клиента обязательно'}), 400
        
        client_id = ClientRepository.create(
            name=data['name'],
            email=data.get('email'),
            phone=data.get('phone'),
            status=data.get('status', 'active')
        )
        
        return jsonify({
            'id': client_id,
            'message': 'Клиент успешно создан'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/clients/<int:client_id>', methods=['PUT'])
def update_client(client_id):
    """Обновить данные клиента"""
    try:
        data = request.json
        
        rows_updated = ClientRepository.update(
            client_id=client_id,
            name=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone'),
            status=data.get('status')
        )
        
        if rows_updated == 0:
            return jsonify({'error': 'Клиент не найден'}), 404
        
        return jsonify({'message': 'Клиент успешно обновлен'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/clients/<int:client_id>', methods=['DELETE'])
def delete_client(client_id):
    """Удалить клиента"""
    try:
        rows_deleted = ClientRepository.delete(client_id)
        
        if rows_deleted == 0:
            return jsonify({'error': 'Клиент не найден'}), 404
        
        return jsonify({'message': 'Клиент успешно удален'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============ TRANSACTIONS ENDPOINTS ============

@app.route('/api/transactions', methods=['POST'])
def create_transaction():
    """Создать новую транзакцию"""
    try:
        data = request.json
        
        # Валидация
        if not data.get('client_id'):
            return jsonify({'error': 'ID клиента обязателен'}), 400
        if not data.get('amount'):
            return jsonify({'error': 'Сумма обязательна'}), 400
        if not data.get('direction') or data['direction'] not in ['income', 'expense']:
            return jsonify({'error': 'Направление должно быть income или expense'}), 400
        
        transaction_id = TransactionRepository.create(
            client_id=data['client_id'],
            amount=float(data['amount']),
            category=data.get('category', 'Прочее'),
            direction=data['direction'],
            description=data.get('description'),
            transaction_date=data.get('transaction_date')
        )
        
        return jsonify({
            'id': transaction_id,
            'message': 'Транзакция успешно создана'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/clients/<int:client_id>/transactions', methods=['GET'])
def get_client_transactions(client_id):
    """Получить транзакции клиента"""
    try:
        limit = request.args.get('limit', type=int)
        transactions = TransactionRepository.get_by_client(client_id, limit=limit)
        return jsonify({'transactions': transactions}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============ AI ENDPOINTS ============

@app.route('/api/ai/ask', methods=['POST'])
def ai_ask():
    """Задать вопрос AI ассистенту"""
    try:
        data = request.json
        
        question = data.get('question')
        if not question:
            return jsonify({'error': 'Вопрос не указан'}), 400
        
        client_id = data.get('client_id')
        
        # Отправляем вопрос в AI сервис
        result = ai_service.ask(question=question, client_id=client_id)
        
        if not result['success']:
            return jsonify({
                'error': result.get('error', 'Ошибка при обращении к AI')
            }), 500
        
        # Сохраняем диалог в БД
        AIConversationRepository.create(
            client_id=client_id,
            question=question,
            answer=result['answer'],
            context_data=str(result.get('context_summary'))
        )
        
        return jsonify({
            'answer': result['answer'],
            'model': result['model'],
            'has_context': result['has_context']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/suggestions', methods=['GET'])
def ai_suggestions():
    """Получить предложенные вопросы"""
    try:
        client_id = request.args.get('client_id', type=int)
        suggestions = ai_service.get_suggested_questions(client_id=client_id)
        return jsonify({'suggestions': suggestions}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/conversations', methods=['GET'])
def get_conversations():
    """Получить историю AI диалогов"""
    try:
        client_id = request.args.get('client_id', type=int)
        limit = request.args.get('limit', default=20, type=int)
        
        if client_id:
            conversations = AIConversationRepository.get_by_client(client_id, limit=limit)
        else:
            conversations = AIConversationRepository.get_recent_global(limit=limit)
        
        return jsonify({'conversations': conversations}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============ STATISTICS ENDPOINTS ============

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Получить общую статистику системы"""
    try:
        print("📥 Запрос статистики")
        
        # Статистика клиентов
        total_clients = ClientRepository.get_count()
        print(f"👥 Всего клиентов: {total_clients}")
        
        active_clients = ClientRepository.get_count(status='active')
        print(f"✅ Активных клиентов: {active_clients}")
        
        # Получаем финансовую статистику по всем клиентам
        clients = ClientRepository.get_all()
        print(f"📊 Получено клиентов для статистики: {len(clients)}")
        
        total_income = 0
        total_expense = 0
        total_transactions = 0
        
        for client in clients:
            try:
                summary = TransactionRepository.get_summary(client['id'])
                total_income += summary['total_income']
                total_expense += summary['total_expense']
                total_transactions += summary['transaction_count']
            except Exception as e:
                print(f"⚠️ Ошибка получения транзакций для клиента {client['id']}: {e}")
                continue
        
        print(f"💰 Доходы: {total_income}, Расходы: {total_expense}")
        
        return jsonify({
            'clients': {
                'total': total_clients,
                'active': active_clients,
                'inactive': total_clients - active_clients
            },
            'transactions': {
                'count': total_transactions,
                'income': total_income,
                'expense': total_expense,
                'balance': total_income - total_expense
            }
        }), 200
        
    except Exception as e:
        print(f"❌ ОШИБКА в get_stats: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Проверка работоспособности API"""
    return jsonify({
        'status': 'ok',
        'service': 'AI CRM API',
        'version': '1.0.0'
    }), 200


# ============ ERROR HANDLERS ============

@app.errorhandler(404)
def not_found(error):
    """Обработчик 404 ошибки"""
    return jsonify({'error': 'Endpoint не найден'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Обработчик 500 ошибки"""
    return jsonify({'error': 'Внутренняя ошибка сервера'}), 500


# ============ MAIN ============

if __name__ == '__main__':
    print("🚀 Запуск AI CRM API сервера...")
    print(f"📍 URL: http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
    print(f"🤖 AI модель: {Config.AI_MODEL}")
    print(f"💾 База данных: {Config.DATABASE_FILE}")
    print("-" * 50)
    
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG
    )
