# repositories.py
"""
Репозитории для работы с данными
Адаптировано под банковскую и CRM структуру
РАЗДЕЛЕНИЕ ПО БАНКАМ: каждая комбинация client_id + bank_code = отдельный клиент
"""

from typing import List, Optional, Dict
from datetime import datetime, timedelta
from database import db_manager
from config import Config


class ClientRepository:
    """Репозиторий для работы с клиентами"""
    
    @staticmethod
    def _detect_structure():
        """Определить структуру таблицы clients"""
        try:
            columns = [row['name'] for row in db_manager.execute_query("PRAGMA table_info(clients)")]
            result = 'banking' if 'bank_code' in columns else 'crm'
            return result
        except Exception as e:
            print(f"❌ Ошибка _detect_structure: {e}")
            return 'crm'
    
    @staticmethod
    def _assign_mock_contacts(clients: List[Dict]) -> List[Dict]:
        """
        Присваивает рандомные email и phone из .env клиентам
        Если клиентов больше чем контактов - циклически повторяет контакты
        """
        mock_contacts = Config.get_mock_contacts()
        
        if not mock_contacts:
            return clients
        
        # Создаем копию списка клиентов для модификации
        clients_with_contacts = []
        
        for idx, client in enumerate(clients):
            client_copy = dict(client)
            
            # Если email/phone уже есть и не null - пропускаем
            has_email = client.get('email') and str(client.get('email')).lower() != 'null'
            has_phone = client.get('phone') and str(client.get('phone')).lower() != 'null'
            
            if not has_email or not has_phone:
                # Циклически выбираем контакт (если клиентов больше - повторяем)
                contact_idx = idx % len(mock_contacts)
                email, phone = mock_contacts[contact_idx]
                
                if not has_email:
                    client_copy['email'] = email
                if not has_phone:
                    client_copy['phone'] = phone
            
            clients_with_contacts.append(client_copy)
        
        return clients_with_contacts
    
    @staticmethod
    def get_all(status: Optional[str] = None) -> List[Dict]:
        """Получить всех клиентов"""
        structure = ClientRepository._detect_structure()
        
        if structure == 'banking':
            # РАЗДЕЛЕНИЕ: каждая комбинация client_id + bank_code = отдельный клиент
            query = '''
                SELECT 
                    c.client_id || '-' || c.bank_code as id,
                    c.client_id || ' (' || c.bank_code || ')' as name,
                    c.client_id as client_id_original,
                    c.bank_code as bank_code,
                    'active' as status,
                    c.created_at as created_at,
                    c.created_at as updated_at,
                    NULL as email,
                    NULL as phone
                FROM clients c
                GROUP BY c.client_id, c.bank_code
                ORDER BY c.bank_code, c.client_id
            '''
            clients = db_manager.execute_query(query)
            
            # Добавляем мок-контакты
            clients = ClientRepository._assign_mock_contacts(clients)
            
            return clients
            
        else:
            # CRM структура
            if status:
                query = '''
                    SELECT id, name, email, phone, status, created_at, updated_at
                    FROM clients 
                    WHERE status = ?
                    ORDER BY id DESC
                '''
                return db_manager.execute_query(query, (status,))
            else:
                query = '''
                    SELECT id, name, email, phone, status, created_at, updated_at
                    FROM clients 
                    ORDER BY id DESC
                '''
                return db_manager.execute_query(query)
    
    @staticmethod
    def get_by_id(client_id: str) -> Optional[Dict]:
        """Получить клиента по ID (составной: client_id-bank_code)"""
        structure = ClientRepository._detect_structure()
        
        if structure == 'banking':
            # Разбираем составной ID: client_id-bank_code
            if '-' in str(client_id):
                parts = str(client_id).rsplit('-', 1)
                if len(parts) == 2:
                    client_id_part, bank_code = parts
                else:
                    client_id_part = client_id
                    bank_code = None
            else:
                client_id_part = client_id
                bank_code = None
            
            if bank_code:
                query = '''
                    SELECT 
                        c.client_id || '-' || c.bank_code as id,
                        c.client_id || ' (' || c.bank_code || ')' as name,
                        c.client_id as client_id_original,
                        c.bank_code as bank_code,
                        'active' as status,
                        c.created_at as created_at,
                        c.created_at as updated_at,
                        NULL as email,
                        NULL as phone
                    FROM clients c
                    WHERE c.client_id = ? AND c.bank_code = ?
                    LIMIT 1
                '''
                results = db_manager.execute_query(query, (client_id_part, bank_code))
            else:
                query = '''
                    SELECT 
                        c.client_id || '-' || c.bank_code as id,
                        c.client_id || ' (' || c.bank_code || ')' as name,
                        c.client_id as client_id_original,
                        c.bank_code as bank_code,
                        'active' as status,
                        c.created_at as created_at,
                        c.created_at as updated_at,
                        NULL as email,
                        NULL as phone
                    FROM clients c
                    WHERE c.client_id = ?
                    LIMIT 1
                '''
                results = db_manager.execute_query(query, (client_id_part,))
            
            # Добавляем мок-контакты для одного клиента
            if results:
                results = ClientRepository._assign_mock_contacts(results)
                
        else:
            query = '''
                SELECT id, name, email, phone, status, created_at, updated_at
                FROM clients 
                WHERE id = ?
            '''
            results = db_manager.execute_query(query, (str(client_id),))
        
        return results[0] if results else None
    
    @staticmethod
    def create(name: str, email: str = None, phone: str = None, 
           status: str = 'active') -> str:
        """
        Создать нового клиента
        В банковском режиме создаём "обычного" клиента с id = uuid, без bank_code
        """
        structure = ClientRepository._detect_structure()
        
        if structure == 'banking':
            # Создаём клиента как в обычной CRM — просто без bank_code
            query = '''
                INSERT INTO clients (client_id, bank_code, created_at)
                VALUES (?, ?, datetime('now'))
            '''
            # Генерируем простой UUID-подобный id
            import uuid
            new_id = str(uuid.uuid4())[:8]
            db_manager.execute_update(query, (new_id, 'MANUAL'))
            
            # Возвращаем составной id в формате, который понимает фронтенд
            return f"{new_id}-MANUAL"
        
        else:
            # Обычная CRM логика
            query = '''
                INSERT INTO clients (name, email, phone, status)
                VALUES (?, ?, ?, ?)
            '''
            client_id = db_manager.execute_update(query, (name, email, phone, status))
            return str(client_id)
    
    @staticmethod
    def update(client_id: int, name: str = None, email: str = None,
               phone: str = None, status: str = None) -> int:
        """Обновить данные клиента (только для CRM)"""
        structure = ClientRepository._detect_structure()
        
        if structure == 'banking':
            return 0
        
        updates = []
        params = []
        
        if name is not None:
            updates.append('name = ?')
            params.append(name)
        
        if email is not None:
            updates.append('email = ?')
            params.append(email)
        
        if phone is not None:
            updates.append('phone = ?')
            params.append(phone)
        
        if status is not None:
            updates.append('status = ?')
            params.append(status)
        
        if not updates:
            return 0
        
        updates.append('updated_at = CURRENT_TIMESTAMP')
        params.append(client_id)
        
        query = f'''
            UPDATE clients 
            SET {', '.join(updates)}
            WHERE id = ?
        '''
        return db_manager.execute_update(query, tuple(params))
    
    @staticmethod
    def delete(client_id: int) -> int:
        """Удалить клиента (только для CRM)"""
        structure = ClientRepository._detect_structure()
        
        if structure == 'banking':
            return 0
        
        query = 'DELETE FROM clients WHERE id = ?'
        return db_manager.execute_update(query, (client_id,))
    
    @staticmethod
    def get_count(status: Optional[str] = None) -> int:
        """Получить количество клиентов"""
        structure = ClientRepository._detect_structure()
        
        if structure == 'banking':
            # Считаем уникальные комбинации client_id + bank_code
            query = 'SELECT COUNT(*) as count FROM (SELECT DISTINCT client_id, bank_code FROM clients)'
            result = db_manager.execute_query(query)
            return result[0]['count'] if result else 0
        else:
            if status:
                query = 'SELECT COUNT(*) as count FROM clients WHERE status = ?'
                result = db_manager.execute_query(query, (status,))
            else:
                query = 'SELECT COUNT(*) as count FROM clients'
                result = db_manager.execute_query(query)
            
            return result[0]['count'] if result else 0


class TransactionRepository:
    """Репозиторий для работы с транзакциями"""
    
    @staticmethod
    def _detect_structure():
        """Определить структуру таблицы transactions"""
        try:
            columns = [row['name'] for row in db_manager.execute_query("PRAGMA table_info(transactions)")]
            result = 'banking' if ('credit_debit_indicator' in columns or 'transaction_id' in columns) else 'crm'
            return result
        except:
            return 'crm'
    
    @staticmethod
    def get_by_client(client_id: str, limit: Optional[int] = None) -> List[Dict]:
        """Получить транзакции клиента (с учетом банка)"""
        try:
            # Получаем колонки
            all_columns = db_manager.execute_query("PRAGMA table_info(transactions)")
            column_names = [col['name'] for col in all_columns]
            
            # Определяем колонку даты
            if 'booking_date_time' in column_names:
                date_col = 'booking_date_time'
            elif 'value_date_time' in column_names:
                date_col = 'value_date_time'
            elif 'created_at' in column_names:
                date_col = 'created_at'
            else:
                date_col = 'id'
            
            # Разбираем составной ID (client_id-bank_code)
            if '-' in str(client_id):
                parts = str(client_id).rsplit('-', 1)
                if len(parts) == 2:
                    client_id_part, bank_code = parts
                else:
                    client_id_part = client_id
                    bank_code = None
            else:
                client_id_part = client_id
                bank_code = None
            
            # Если есть банковские колонки
            if 'transaction_id' in column_names and 'client_id' in column_names:
                if bank_code:
                    # Фильтр по client_id И bank_code
                    query = f'''
                        SELECT 
                            t.transaction_id as id,
                            t.client_id as client_id,
                            t.bank_code,
                            t.amount,
                            COALESCE(t.transaction_information, 'Без категории') as category,
                            t.credit_debit_indicator as direction,
                            COALESCE(t.transaction_information, '') as description,
                            DATE(t.{date_col}) as transaction_date,
                            t.created_at as created_at
                        FROM transactions t
                        WHERE t.client_id = ? AND t.bank_code = ?
                        ORDER BY t.{date_col} DESC
                    '''
                    params = (client_id_part, bank_code)
                else:
                    # Фильтр только по client_id (все банки)
                    query = f'''
                        SELECT 
                            t.transaction_id as id,
                            t.client_id as client_id,
                            t.bank_code,
                            t.amount,
                            COALESCE(t.transaction_information, 'Без категории') as category,
                            t.credit_debit_indicator as direction,
                            COALESCE(t.transaction_information, '') as description,
                            DATE(t.{date_col}) as transaction_date,
                            t.created_at as created_at
                        FROM transactions t
                        WHERE t.client_id = ?
                        ORDER BY t.{date_col} DESC
                    '''
                    params = (client_id_part,)
            else:
                # CRM структура
                query = '''
                    SELECT id, client_id, amount, category, direction, 
                           description, transaction_date, created_at
                    FROM transactions
                    WHERE client_id = ?
                    ORDER BY transaction_date DESC, created_at DESC
                '''
                params = (str(client_id),)
            
            if limit:
                query += f' LIMIT {limit}'
            
            result = db_manager.execute_query(query, params)
            return result
            
        except Exception as e:
            print(f"❌ Ошибка get_by_client: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    @staticmethod
    def create(client_id: int, amount: float, category: str, 
               direction: str, description: str = None,
               transaction_date: str = None) -> int:
        """Создать транзакцию (только для CRM)"""
        structure = TransactionRepository._detect_structure()
        
        if structure == 'banking':
            raise Exception("Используйте банковский API для создания транзакций")
        
        if transaction_date:
            query = '''
                INSERT INTO transactions 
                (client_id, amount, category, direction, description, transaction_date)
                VALUES (?, ?, ?, ?, ?, ?)
            '''
            params = (client_id, amount, category, direction, description, transaction_date)
        else:
            query = '''
                INSERT INTO transactions 
                (client_id, amount, category, direction, description)
                VALUES (?, ?, ?, ?, ?)
            '''
            params = (client_id, amount, category, direction, description)
        
        return db_manager.execute_update(query, params)
    
    @staticmethod
    def get_summary(client_id: str) -> Dict:
        """Получить финансовую сводку клиента (с учетом банка)"""
        structure = TransactionRepository._detect_structure()
        
        # Разбираем составной ID
        if '-' in str(client_id):
            parts = str(client_id).rsplit('-', 1)
            if len(parts) == 2:
                client_id_part, bank_code = parts
            else:
                client_id_part = client_id
                bank_code = None
        else:
            client_id_part = client_id
            bank_code = None
        
        if structure == 'banking':
            if bank_code:
                query = '''
                    SELECT 
                        SUM(CASE WHEN credit_debit_indicator = 'Credit' THEN amount ELSE 0 END) as total_income,
                        SUM(CASE WHEN credit_debit_indicator = 'Debit' THEN amount ELSE 0 END) as total_expense,
                        COUNT(*) as transaction_count
                    FROM transactions
                    WHERE client_id = ? AND bank_code = ?
                '''
                result = db_manager.execute_query(query, (client_id_part, bank_code))
            else:
                query = '''
                    SELECT 
                        SUM(CASE WHEN credit_debit_indicator = 'Credit' THEN amount ELSE 0 END) as total_income,
                        SUM(CASE WHEN credit_debit_indicator = 'Debit' THEN amount ELSE 0 END) as total_expense,
                        COUNT(*) as transaction_count
                    FROM transactions
                    WHERE client_id = ?
                '''
                result = db_manager.execute_query(query, (client_id_part,))
        else:
            query = '''
                SELECT 
                    SUM(CASE WHEN direction = 'income' THEN amount ELSE 0 END) as total_income,
                    SUM(CASE WHEN direction = 'expense' THEN amount ELSE 0 END) as total_expense,
                    COUNT(*) as transaction_count
                FROM transactions
                WHERE client_id = ?
            '''
            result = db_manager.execute_query(query, (str(client_id),))
        
        if result:
            data = result[0]
            return {
                'total_income': data['total_income'] or 0,
                'total_expense': data['total_expense'] or 0,
                'balance': (data['total_income'] or 0) - (data['total_expense'] or 0),
                'transaction_count': data['transaction_count'] or 0
            }
        
        return {
            'total_income': 0,
            'total_expense': 0,
            'balance': 0,
            'transaction_count': 0
        }
    
    @staticmethod
    def get_by_category(client_id: str) -> List[Dict]:
        """Получить статистику по категориям (с учетом банка)"""
        structure = TransactionRepository._detect_structure()
        
        # Разбираем составной ID
        if '-' in str(client_id):
            parts = str(client_id).rsplit('-', 1)
            if len(parts) == 2:
                client_id_part, bank_code = parts
            else:
                client_id_part = client_id
                bank_code = None
        else:
            client_id_part = client_id
            bank_code = None
        
        if structure == 'banking':
            if bank_code:
                query = '''
                    SELECT 
                        COALESCE(transaction_information, 'Без категории') as category,
                        credit_debit_indicator as direction,
                        SUM(amount) as total,
                        COUNT(*) as count
                    FROM transactions
                    WHERE client_id = ? AND bank_code = ?
                    GROUP BY transaction_information, credit_debit_indicator
                    ORDER BY total DESC
                '''
                return db_manager.execute_query(query, (client_id_part, bank_code))
            else:
                query = '''
                    SELECT 
                        COALESCE(transaction_information, 'Без категории') as category,
                        credit_debit_indicator as direction,
                        SUM(amount) as total,
                        COUNT(*) as count
                    FROM transactions
                    WHERE client_id = ?
                    GROUP BY transaction_information, credit_debit_indicator
                    ORDER BY total DESC
                '''
                return db_manager.execute_query(query, (client_id_part,))
        else:
            query = '''
                SELECT 
                    category,
                    direction,
                    SUM(amount) as total,
                    COUNT(*) as count
                FROM transactions
                WHERE client_id = ?
                GROUP BY category, direction
                ORDER BY total DESC
            '''
            return db_manager.execute_query(query, (str(client_id),))
    @staticmethod
    def get_average_balance() -> float:
        """Получить средний баланс всех клиентов"""
        try:
            clients = ClientRepository.get_all()
            if not clients:
                return 0.0
            
            balances = []
            for client in clients:
                summary = TransactionRepository.get_summary(client['id'])
                balances.append(summary['balance'])
            
            avg = sum(balances) / len(balances) if balances else 0.0
            return avg
        except Exception as e:
            print(f"❌ Ошибка get_average_balance: {e}")
            return 0.0

    @staticmethod
    def calculate_client_rating(client_id: str) -> float:
        """
        Расчет рейтинга клиента (формула на квадратном корне для более мягкого распределения)
        Рейтинг от 1.0 до 5.0 на основе баланса относительно других клиентов
        """
        import math
        
        try:
            # Получаем баланс клиента
            summary = TransactionRepository.get_summary(client_id)
            client_balance = summary['balance']
            
            # Получаем балансы всех клиентов
            clients = ClientRepository.get_all()
            if not clients or len(clients) == 0:
                return 3.0
            
            balances = []
            for client in clients:
                client_summary = TransactionRepository.get_summary(client['id'])
                balances.append(client_summary['balance'])
            
            if not balances:
                return 3.0
            
            max_balance = max(balances)
            avg_balance = sum(balances) / len(balances)
            
            # Защита от деления на ноль
            if max_balance <= 0 or avg_balance <= 0:
                return 3.0
            
            # Формула на квадратном корне для более мягкого распределения
            ratio = math.sqrt(max(0, client_balance) / avg_balance)
            max_ratio = math.sqrt(max_balance / avg_balance)
            
            if max_ratio == 0:
                return 3.0
            
            rating = 1 + 4 * (ratio / max_ratio)
            
            # Ограничиваем от 1.0 до 5.0
            rating = max(1.0, min(5.0, rating))
            
            return round(rating, 1)
        except Exception as e:
            print(f"❌ Ошибка calculate_client_rating для {client_id}: {e}")
            return 3.0



class AIConversationRepository:
    """Репозиторий для работы с AI диалогами"""
    
    @staticmethod
    def get_by_client(client_id: int, limit: int = 10) -> List[Dict]:
        """Получить историю диалогов клиента"""
        query = '''
            SELECT id, client_id, question, answer, context_data, created_at
            FROM ai_conversations
            WHERE client_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        '''
        return db_manager.execute_query(query, (str(client_id), limit))
    
    @staticmethod
    def create(client_id: Optional[int], question: str, 
               answer: str, context_data: str = None) -> int:
        """Сохранить диалог"""
        query = '''
            INSERT INTO ai_conversations (client_id, question, answer, context_data)
            VALUES (?, ?, ?, ?)
        '''
        return db_manager.execute_update(query, (str(client_id) if client_id else None, question, answer, context_data))
    
    @staticmethod
    def get_recent_global(limit: int = 20) -> List[Dict]:
        """Получить последние диалоги по всем клиентам"""
        query = '''
            SELECT 
                c.id, c.client_id, c.question, c.answer, c.created_at,
                c.client_id as client_name
            FROM ai_conversations c
            ORDER BY c.created_at DESC
            LIMIT ?
        '''
        return db_manager.execute_query(query, (limit,))
