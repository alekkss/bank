# ai_service.py
"""
Сервис для работы с AI (OpenRouter API)
Обработка запросов к AI ассистенту
"""

import requests
import json
from typing import Optional, Dict, List
from config import Config
from repositories import ClientRepository, TransactionRepository


class AIService:
    """Сервис для взаимодействия с AI"""
    
    def __init__(self):
        """Инициализация AI сервиса"""
        self.api_url = Config.AI_API_URL
        self.api_key = Config.AI_API_KEY
        self.model = Config.AI_MODEL
        self.system_prompt = Config.AI_SYSTEM_PROMPT
    
    def _build_context(self, client_id: Optional[int]) -> str:
        """
        Построить контекст для AI на основе данных клиента
        
        Args:
            client_id: ID клиента
            
        Returns:
            str: текстовый контекст с данными
        """
        if not client_id:
            return ""
        
        # Получаем данные клиента
        client = ClientRepository.get_by_id(client_id)
        if not client:
            return ""
        
        # Получаем транзакции
        transactions = TransactionRepository.get_by_client(client_id, limit=50)
        summary = TransactionRepository.get_summary(client_id)
        categories = TransactionRepository.get_by_category(client_id)
        
        # Формируем контекст
        context = f"""
📋 ДАННЫЕ КЛИЕНТА:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 Имя: {client['name']}
📧 Email: {client['email'] or 'Не указан'}
📱 Телефон: {client['phone'] or 'Не указан'}
📊 Статус: {client['status']}

💰 ФИНАНСОВАЯ СВОДКА:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💵 Доходы: {summary['total_income']:,.2f} ₽
💸 Расходы: {summary['total_expense']:,.2f} ₽
📈 Баланс: {summary['balance']:,.2f} ₽
🔢 Всего транзакций: {summary['transaction_count']}

"""
        
        # Добавляем статистику по категориям
        if categories:
            context += "📊 СТАТИСТИКА ПО КАТЕГОРИЯМ:\n"
            context += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            
            income_cats = [c for c in categories if c['direction'] == 'income']
            expense_cats = [c for c in categories if c['direction'] == 'expense']
            
            if income_cats:
                context += "💰 Доходы:\n"
                for cat in income_cats:
                    context += f"  • {cat['category']}: {cat['total']:,.2f} ₽ ({cat['count']} транз.)\n"
                context += "\n"
            
            if expense_cats:
                context += "💸 Расходы:\n"
                for cat in expense_cats:
                    context += f"  • {cat['category']}: {cat['total']:,.2f} ₽ ({cat['count']} транз.)\n"
                context += "\n"
        
        # Добавляем последние транзакции
        if transactions:
            context += "📝 ПОСЛЕДНИЕ ТРАНЗАКЦИИ (топ 10):\n"
            context += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            
            for tx in transactions[:10]:
                emoji = "💚" if tx['direction'] == 'income' else "❤️"
                sign = "+" if tx['direction'] == 'income' else "-"
                context += f"{emoji} {tx['transaction_date']} | {tx['category']}: {sign}{tx['amount']:,.2f} ₽\n"
                if tx['description']:
                    context += f"   💬 {tx['description']}\n"
        
        return context
    
    def ask(self, question: str, client_id: Optional[int] = None) -> Dict:
        """
        Задать вопрос AI ассистенту
        
        Args:
            question: вопрос пользователя
            client_id: ID клиента (опционально)
            
        Returns:
            dict: ответ AI с метаданными
        """
        try:
            # Строим контекст
            context = self._build_context(client_id)
            
            # Формируем сообщения для API
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # Если есть контекст, добавляем его
            if context:
                messages.append({
                    "role": "user",
                    "content": f"Контекст клиента:\n{context}"
                })
                messages.append({
                    "role": "assistant",
                    "content": "✅ Данные получены и проанализированы. Готов отвечать на вопросы!"
                })
            
            # Добавляем вопрос пользователя
            messages.append({
                "role": "user",
                "content": question
            })
            
            # Подготовка запроса к API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": Config.AI_MAX_TOKENS,
                "temperature": Config.AI_TEMPERATURE
            }
            
            # Отправляем запрос
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=Config.AI_TIMEOUT
            )
            
            # Проверяем ответ
            if response.status_code == 200:
                result = response.json()
                answer = result['choices'][0]['message']['content']
                
                return {
                    'success': True,
                    'answer': answer,
                    'model': self.model,
                    'has_context': bool(context),
                    'context_summary': self._get_context_summary(client_id) if client_id else None
                }
            else:
                error_msg = f"AI API вернул ошибку: {response.status_code}"
                if response.text:
                    try:
                        error_data = response.json()
                        error_msg += f" - {error_data.get('error', {}).get('message', '')}"
                    except:
                        pass
                
                return {
                    'success': False,
                    'error': error_msg,
                    'status_code': response.status_code
                }
        
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Превышено время ожидания ответа от AI (30 сек)'
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Ошибка сети: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Неожиданная ошибка: {str(e)}'
            }
    
    def _get_context_summary(self, client_id: int) -> Dict:
        """
        Получить краткую сводку контекста
        
        Args:
            client_id: ID клиента
            
        Returns:
            dict: краткая сводка
        """
        client = ClientRepository.get_by_id(client_id)
        summary = TransactionRepository.get_summary(client_id)
        
        return {
            'client_name': client['name'] if client else None,
            'transaction_count': summary['transaction_count'],
            'balance': summary['balance']
        }
    
    def get_suggested_questions(self, client_id: Optional[int] = None) -> List[str]:
        """
        Получить предложенные вопросы для клиента
        
        Args:
            client_id: ID клиента
            
        Returns:
            list: список предложенных вопросов
        """
        if client_id:
            summary = TransactionRepository.get_summary(client_id)
            
            questions = [
                "📊 Проанализируй мои расходы за последний период",
                "💡 Дай рекомендации по оптимизации бюджета",
                "📈 Какие категории расходов самые большие?",
                "💰 Как я могу увеличить свои сбережения?",
            ]
            
            if summary['transaction_count'] > 10:
                questions.append("📉 Найди паттерны в моих тратах")
            
            if summary['balance'] < 0:
                questions.append("⚠️ У меня отрицательный баланс, что делать?")
            
            return questions
        else:
            return [
                "❓ Как работает эта CRM система?",
                "📊 Покажи общую статистику",
                "💡 Какие возможности у AI ассистента?",
                "🔍 Как добавить нового клиента?"
            ]


# Создаем единственный экземпляр сервиса
ai_service = AIService()
