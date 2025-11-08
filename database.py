# database.py
"""
Модуль для работы с базой данных SQLite
Совместимость со старой структурой из base.py
"""

import sqlite3
import os
from typing import Optional
from contextlib import contextmanager
from config import Config


class DatabaseManager:
    """Менеджер базы данных"""
    
    def __init__(self, db_file: str = None):
        """Инициализация менеджера БД"""
        self.db_file = db_file or Config.DATABASE_FILE
        self.db_exists = os.path.exists(self.db_file)
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Контекстный менеджер для работы с подключением к БД"""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def check_existing_structure(self):
        """Проверить структуру существующей БД"""
        if not self.db_exists:
            return None
            
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Получаем список таблиц
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table'
            """)
            tables = {row[0] for row in cursor.fetchall()}
            
            # Если есть старая структура (банковская)
            if 'banks' in tables and 'accounts' in tables:
                cursor.execute("PRAGMA table_info(transactions)")
                columns = {row[1] for row in cursor.fetchall()}
                return {
                    'type': 'banking',
                    'tables': tables,
                    'transaction_columns': columns
                }
            
            # Если есть новая структура (CRM)
            if 'clients' in tables:
                cursor.execute("PRAGMA table_info(clients)")
                columns = {row[1] for row in cursor.fetchall()}
                
                # Определяем тип по колонкам
                if 'email' in columns and 'phone' in columns:
                    return {
                        'type': 'crm',
                        'tables': tables,
                        'client_columns': columns
                    }
                else:
                    return {
                        'type': 'banking',
                        'tables': tables,
                        'client_columns': columns
                    }
            
            return None
    
    def init_database(self):
        """Инициализация базы данных"""
        structure = self.check_existing_structure()
        
        if structure:
            if structure['type'] == 'banking':
                print(f"✅ Обнаружена банковская БД: {self.db_file}")
                print(f"📊 Таблицы: {', '.join(structure['tables'])}")
                self._add_ai_conversations_table()
            elif structure['type'] == 'crm':
                print(f"✅ Обнаружена CRM БД: {self.db_file}")
                self._ensure_crm_structure()
        else:
            print(f"🆕 Создается новая CRM база данных: {self.db_file}")
            self._create_crm_database()
    
    def _add_ai_conversations_table(self):
        """Добавить таблицу AI диалогов в существующую БД"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='ai_conversations'
            """)
            
            if not cursor.fetchone():
                print("➕ Добавление таблицы ai_conversations")
                cursor.execute('''
                    CREATE TABLE ai_conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        client_id TEXT,
                        question TEXT NOT NULL,
                        answer TEXT NOT NULL,
                        context_data TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_conversations_client 
                    ON ai_conversations(client_id)
                ''')
                print("✅ Таблица ai_conversations создана")
    
    def _ensure_crm_structure(self):
        """Проверить и дополнить CRM структуру"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Проверяем наличие необходимых таблиц
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN ('clients', 'ai_conversations')
            """)
            existing_tables = {row[0] for row in cursor.fetchall()}
            
            if 'ai_conversations' not in existing_tables:
                self._add_ai_conversations_table()
    
    def _create_crm_database(self):
        """Создать новую CRM базу данных"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Таблица клиентов (простая CRM структура)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print("✅ Создана таблица clients")
            
            # Таблица транзакций (простая CRM структура)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    direction TEXT NOT NULL CHECK(direction IN ('income', 'expense')),
                    description TEXT,
                    transaction_date DATE DEFAULT CURRENT_DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE
                )
            ''')
            print("✅ Создана таблица transactions")
            
            # Таблица AI диалогов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    context_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE
                )
            ''')
            print("✅ Создана таблица ai_conversations")
            
            # Индексы
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_transactions_client 
                ON transactions(client_id)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_transactions_date 
                ON transactions(transaction_date)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_conversations_client 
                ON ai_conversations(client_id)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_clients_status 
                ON clients(status)
            ''')
            print("✅ Созданы индексы")
    
    def execute_query(self, query: str, params: tuple = ()) -> list:
        """Выполнить SELECT запрос"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Выполнить INSERT/UPDATE/DELETE запрос"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.lastrowid if cursor.lastrowid else cursor.rowcount
    
    def get_table_stats(self) -> dict:
        """Получить статистику по таблицам"""
        stats = {}
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Получаем список всех таблиц
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables:
                try:
                    cursor.execute(f'SELECT COUNT(*) as count FROM {table}')
                    stats[table] = cursor.fetchone()[0]
                except:
                    stats[table] = 0
        
        return stats
    
    def clear_table(self, table_name: str):
        """Очистить таблицу"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'DELETE FROM {table_name}')
            cursor.execute(f'DELETE FROM sqlite_sequence WHERE name="{table_name}"')


# Создаем единственный экземпляр менеджера БД
db_manager = DatabaseManager()
