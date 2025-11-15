# ai_service.py

"""
AI сервис для обработки запросов через OpenRouter API
Интеграция с AI моделями для умных ответов
"""

import requests
import json
from typing import Optional, Dict, List
from config import Config
from repositories import ClientRepository, TransactionRepository

class AIService:
    """AI сервис"""
    
    def __init__(self):
        """Инициализация AI сервиса"""
        self.api_url = Config.AI_API_URL
        self.api_key = Config.AI_API_KEY
        self.model = Config.AI_MODEL
        self.system_prompt = Config.AI_SYSTEM_PROMPT
    
    def _normalize_direction(self, direction: str) -> str:
        """
        Нормализует направление транзакции для унифицированной обработки
        
        Args:
            direction: Credit/Debit или income/expense
            
        Returns:
            'income' или 'expense'
        """
        direction_lower = direction.lower()
        if direction_lower in ['credit', 'income']:
            return 'income'
        elif direction_lower in ['debit', 'expense']:
            return 'expense'
        return direction_lower
    
    def build_context(self, client_id: Optional[str]) -> str:
        """
        Построить контекст для AI на основе данных клиента
        
        Args:
            client_id: ID клиента
            
        Returns:
            str: Контекст для AI
        """
        if not client_id:
            return ""
        
        # Получаем данные клиента
        client = ClientRepository.get_by_id(client_id)
        if not client:
            return ""
        
        # Получаем транзакции и статистику
        transactions = TransactionRepository.get_by_client(client_id, limit=50)
        summary = TransactionRepository.get_summary(client_id)
        categories = TransactionRepository.get_by_category(client_id)
        
        # Формируем контекст
        context = f"""Данные клиента:
- Имя клиента: {client['name']}
- Email: {client['email'] or 'Не указан'}
- Телефон: {client['phone'] or 'Не указан'}
- Статус: {client['status']}

Финансовая сводка:
- Общий доход: {summary['total_income']:,.2f} ₽
- Общие расходы: {summary['total_expense']:,.2f} ₽
- Баланс: {summary['balance']:,.2f} ₽
- Всего транзакций: {summary['transaction_count']}
"""
        
        # Добавляем категории
        if categories:
            context += "\nТранзакции по категориям:\n"
            
            # Разделяем на доходы и расходы
            income_cats = [c for c in categories if self._normalize_direction(c['direction']) == 'income']
            expense_cats = [c for c in categories if self._normalize_direction(c['direction']) == 'expense']
            
            if income_cats:
                context += "\nДоходы:\n"
                for cat in income_cats:
                    context += f"  💰 {cat['category']}: +{cat['total']:,.2f} ₽ ({cat['count']} транзакций)\n"
            
            if expense_cats:
                context += "\nРасходы:\n"
                for cat in expense_cats:
                    context += f"  💸 {cat['category']}: -{cat['total']:,.2f} ₽ ({cat['count']} транзакций)\n"
        
        # Добавляем последние 10 транзакций
        if transactions:
            context += f"\nПоследние 10 транзакций:\n"
            for tx in transactions[:10]:
                # Определяем направление
                normalized_direction = self._normalize_direction(tx['direction'])
                emoji = "💰" if normalized_direction == 'income' else "💸"
                sign = "+" if normalized_direction == 'income' else "-"
                
                context += f"  {emoji} {tx['transaction_date']} | {tx['category']} | {sign}{tx['amount']:,.2f} ₽"
                
                if tx.get('description'):
                    context += f" | {tx['description']}"
                
                context += "\n"
        
        return context
    
    def ask(self, question: str, client_id: Optional[str] = None) -> Dict:
        """
        Задать вопрос AI
        
        Args:
            question: Вопрос пользователя
            client_id: ID клиента (опционально)
            
        Returns:
            dict: Результат от AI
        """
        try:
            # Строим контекст
            context = self.build_context(client_id)
            
            # Формируем сообщения
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # Добавляем контекст через API
            if context:
                messages.append({
                    "role": "user",
                    "content": f"Контекст:\n{context}"
                })
                messages.append({
                    "role": "assistant",
                    "content": "Понял. Готов ответить на вопросы по этому клиенту!"
                })
            
            # Добавляем вопрос пользователя
            messages.append({
                "role": "user",
                "content": question
            })
            
            # Готовим запрос
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
            
            # Отправляем запрос в API
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=Config.AI_TIMEOUT
            )
            
            # Обрабатываем ответ
            if response.status_code == 200:
                result = response.json()
                answer = result['choices'][0]['message']['content']
                
                return {
                    'success': True,
                    'answer': answer,
                    'model': self.model,
                    'has_context': bool(context),
                    'context_summary': self.get_context_summary(client_id) if client_id else None
                }
            else:
                error_msg = f"AI API ошибка: {response.status_code}"
                if response.text:
                    try:
                        error_data = response.json()
                        error_msg = f"{error_msg} - {error_data.get('error', {}).get('message', '')}"
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
                'error': 'AI сервис не отвечает (таймаут 30 сек)'
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Ошибка подключения к AI: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Непредвиденная ошибка: {str(e)}'
            }
    
    def get_context_summary(self, client_id: str) -> Dict:
        """
        Получить краткую сводку контекста
        
        Args:
            client_id: ID клиента
            
        Returns:
            dict: Краткая сводка
        """
        client = ClientRepository.get_by_id(client_id)
        summary = TransactionRepository.get_summary(client_id)
        
        return {
            'client_name': client['name'] if client else None,
            'transaction_count': summary['transaction_count'],
            'balance': summary['balance']
        }
    
    def get_suggested_questions(self, client_id: Optional[str] = None) -> List[str]:
        """
        Получить предложенные вопросы
        
        Args:
            client_id: ID клиента (опционально)
            
        Returns:
            list: Список предложенных вопросов
        """
        if client_id:
            summary = TransactionRepository.get_summary(client_id)
            
            questions = [
                "Проанализируй расходы клиента",
                "Какие основные категории доходов?",
                "Есть ли необычные транзакции?",
                "Дай рекомендации по оптимизации расходов"
            ]
            
            if summary['transaction_count'] > 10:
                questions.append("Покажи динамику транзакций")
            
            if summary['balance'] < 0:
                questions.append("Почему баланс отрицательный?")
            
            return questions
        else:
            return [
                "Сколько всего клиентов в CRM?",
                "Какая общая статистика по доходам?",
                "Покажи топ клиентов по обороту",
                "Как работает AI ассистент?"
            ]

# Глобальный экземпляр
ai_service = AIService()
