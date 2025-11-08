# repositories.py
"""
Репозитории для работы с данными
Адаптировано под банковскую и CRM структуру
РАЗДЕЛЕНИЕ ПО БАНКАМ: каждая комбинация client_id + bank_code = отдельный клиент
"""

from typing import List, Optional, Dict
from datetime import datetime, timedelta
from database import db_manager


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
            return db_manager.execute_query(query)
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
               status: str = 'active') -> int:
        """Создать нового клиента (только для CRM структуры)"""
        structure = ClientRepository._detect_structure()
        
        if structure == 'banking':
            raise Exception("Используйте банковский API для создания клиентов")
        
        query = '''
            INSERT INTO clients (name, email, phone, status)
            VALUES (?, ?, ?, ?)
        '''
        return db_manager.execute_update(query, (name, email, phone, status))
    
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
