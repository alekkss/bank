"""
base.py - Прямой импорт данных из банковских API в SQLite
Объединяет функционал получения данных из API и создания БД
БЕЗ промежуточного Excel файла
С использованием существующих consent для vbank
"""

import requests
import sqlite3
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class DirectAPIToSQLite:
    """Получение данных из API банков и прямая запись в SQLite"""
    
    def __init__(self, db_file='multibank_real.db'):
        self.db_file = db_file
        self.conn = None
        self.cursor = None

        
        # API credentials
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        
        # Банки
        self.banks = [
            {
                "name": "Awesome Bank",
                "code": "abank",
                "url": "https://abank.open.bankingapi.ru"
            },
            {
                "name": "Virtual Bank",
                "code": "vbank",
                "url": "https://vbank.open.bankingapi.ru"
            }
        ]
        
        # Существующие consent ID для vbank (уже подтверждённые)
        self.vbank_consents = {
            "team047-1": "consent-ebf94ddb5ee9",
            "team047-2": "consent-aa25ea42fc98",
            "team047-3": "consent-de242a679be0",
            "team047-4": "consent-43281571974e",
            "team047-5": "consent-4ee785844d05",
            "team047-6": "consent-574a4e96cf8d",
            "team047-7": "consent-40bd0ca51d3b",
            "team047-8": "consent-bdff43178ac6",
            "team047-9": "consent-2a2931da1e8a",
            "team047-10": "consent-c45178b64ae1"
        }
        
        # Настройки повторов
        self.max_retries = 5
        self.retry_delay = 1.5
        self.request_delay = 0.5
        
        # Статистика
        self.stats = {
            'banks': 0,
            'products': 0,
            'clients': 0,
            'accounts': 0,
            'balances': 0,
            'transactions': 0
        }
    
    
    # ==================== СОЗДАНИЕ БАЗЫ ДАННЫХ ====================
    
    def create_database(self):
        """Создать БД со схемой (если не существует) или переиспользовать существующую"""
        
        db_exists = os.path.exists(self.db_file)
        
        if db_exists:
            print("📊 Подключение к существующей БД...")
            print(f"  ℹ️  БД: {self.db_file}")
            print(f"  🔄 Режим: Обновление данных")
        else:
            print("📊 Создание новой БД...")
            print(f"  ✨ БД: {self.db_file}")
            print(f"  🔄 Режим: Первичная инициализация")
        
        # Подключаемся к БД (создаст файл если не существует)
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()
        
        # Таблица банков
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS banks (
                code TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица клиентов
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id TEXT NOT NULL,
                bank_code TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(client_id, bank_code),
                FOREIGN KEY(bank_code) REFERENCES banks(code)
            )
        ''')
        
        # Таблица счетов
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                account_id TEXT,
                client_id TEXT NOT NULL,
                bank_code TEXT,
                status TEXT,
                currency TEXT,
                account_type TEXT,
                account_subtype TEXT,
                nickname TEXT,
                opening_date TEXT,
                scheme_name TEXT,
                account_number TEXT,
                account_holder_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY(account_id, bank_code),
                FOREIGN KEY(bank_code) REFERENCES banks(code)
            )
        ''')
        
        # Таблица балансов
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS balances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id TEXT NOT NULL,
                client_id TEXT NOT NULL,
                bank_code TEXT NOT NULL,
                balance_type TEXT,
                amount REAL,
                currency TEXT,
                date_time TIMESTAMP,
                credit_debit_indicator TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(account_id, bank_code, balance_type)
            )
        ''')
        
        # Таблица транзакций
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id TEXT NOT NULL,
                account_id TEXT NOT NULL,
                client_id TEXT NOT NULL,
                bank_code TEXT NOT NULL,
                amount REAL,
                currency TEXT,
                credit_debit_indicator TEXT,
                status TEXT,
                booking_date_time TIMESTAMP,
                value_date_time TIMESTAMP,
                transaction_code TEXT,
                transaction_information TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(transaction_id, bank_code)
            )
        ''')
        
        # Таблица продуктов
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                product_id TEXT,
                product_type TEXT,
                product_name TEXT,
                description TEXT,
                interest_rate REAL,
                min_amount REAL,
                max_amount REAL,
                term_months INTEGER,
                bank_code TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY(product_id, bank_code)
            )
        ''')
        
        self.conn.commit()
        
        if db_exists:
            print("  ✓ Подключено к существующей БД")
            print("  💡 Новые данные будут добавлены/обновлены\n")
        else:
            print("  ✓ БД схема создана\n")
    
    
    # ==================== API МЕТОДЫ ====================
    
    def get_token(self, bank_url):
        """Получить токен для банка"""
        try:
            response = requests.post(
                f"{bank_url}/auth/bank-token",
                params={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token') or data.get('bank_token')
                return token
            else:
                print(f"  ❌ Токен не получен (status: {response.status_code})")
                return None
        except Exception as e:
            print(f"  ❌ Ошибка получения токена: {e}")
            return None
    
    
    def get_products(self, bank_url, bank_code):
        """Получить продукты банка и сохранить в БД"""
        try:
            response = requests.get(f"{bank_url}/products", timeout=10)
            if response.status_code == 200:
                data = response.json()
                products = data.get('data', {}).get('product', [])
                
                # Сохраняем продукты в БД
                for product in products:
                    try:
                        self.cursor.execute('''
                            INSERT OR REPLACE INTO products
                            (product_id, product_type, product_name, description,
                             interest_rate, min_amount, max_amount, term_months, bank_code)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            product.get('productId'),
                            product.get('productType'),
                            product.get('productName'),
                            product.get('description', ''),
                            product.get('interestRate'),
                            product.get('minAmount'),
                            product.get('maxAmount'),
                            product.get('termMonths'),
                            bank_code
                        ))
                        self.stats['products'] += 1
                    except Exception as e:
                        print(f"  ⚠️ Ошибка сохранения продукта: {e}")
                
                self.conn.commit()
                return len(products)
            return 0
        except Exception as e:
            print(f"  ⚠️ Ошибка получения продуктов: {e}")
            return 0
    
    
    def create_consent_with_retry(self, bank_url, token, client_id, bank_code):
        """Создать согласие или использовать существующее для vbank"""
        
        # Для vbank - используем существующий consent
        if bank_code == 'vbank':
            existing_consent = self.vbank_consents.get(client_id)
            if existing_consent:
                print(f"    ✓ Используем существующий consent: {existing_consent}")
                return existing_consent
            else:
                print(f"    ⚠️ Нет consent для {client_id}")
                return None
        
        # Для abank - создаём новый (автоматически)
        for attempt in range(self.max_retries):
            try:
                payload = {
                    "client_id": client_id,
                    "permissions": [
                        "ReadAccountsBasic",
                        "ReadAccountsDetail",
                        "ReadBalances",
                        "ReadTransactionsBasic",
                        "ReadTransactionsDetail"
                    ],
                    "reason": "",
                    "requesting_bank": f"{bank_code}_bank",
                    "requesting_bank_name": "Test Bank"
                }
                
                headers = {
                    'Authorization': f'Bearer {token}',
                    'X-Requesting-Bank': self.client_id,
                    'Content-Type': 'application/json',
                    'accept': 'application/json'
                }
                
                response = requests.post(
                    f"{bank_url}/account-consents/request",
                    json=payload,
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    consent_id = data.get('consent_id') or data.get('consentId')
                    if consent_id:
                        print(f"    ✓ Consent ID: {consent_id}")
                        return consent_id
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except Exception as e:
                print(f"    ⚠️ Ошибка создания согласия: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        return None
    
    
    def get_accounts_with_retry(self, bank_url, token, client_id, consent_id):
        """Получить счета с повторами если пусто"""
        for attempt in range(self.max_retries):
            headers = {
                'Authorization': f'Bearer {token}',
                'X-Requesting-Bank': self.client_id,
                'X-Consent-Id': consent_id
            }
            
            time.sleep(self.request_delay)
            try:
                response = requests.get(
                    f"{bank_url}/accounts",
                    params={'client_id': client_id},
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    accounts = data if isinstance(data, list) else data.get('data', {}).get('account', [])
                    if accounts:
                        return accounts
                
                if attempt < self.max_retries - 1:
                    print(f"  ⏳ Попытка {attempt + 1}/{self.max_retries}: счетов нет, повтор...")
                    time.sleep(self.retry_delay)
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        return []
    
    
    def get_balances(self, bank_url, token, account_id, consent_id):
        """Получить балансы"""
        headers = {
            'Authorization': f'Bearer {token}',
            'X-Requesting-Bank': self.client_id,
            'X-Consent-Id': consent_id
        }
        
        time.sleep(self.request_delay)
        try:
            response = requests.get(
                f"{bank_url}/accounts/{account_id}/balances",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                balances = data if isinstance(data, list) else data.get('data', {}).get('balance', [])
                return balances
        except Exception as e:
            pass
        
        return []
    
    
    def get_transactions_with_retry(self, bank_url, token, account_id, consent_id):
        """Получить транзакции с повторами если пусто"""
        for attempt in range(self.max_retries):
            headers = {
                'Authorization': f'Bearer {token}',
                'X-Requesting-Bank': self.client_id,
                'X-Consent-Id': consent_id
            }
            
            time.sleep(self.request_delay)
            try:
                response = requests.get(
                    f"{bank_url}/accounts/{account_id}/transactions",
                    params={'limit': 100, 'page': 1},
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    transactions = data if isinstance(data, list) else data.get('data', {}).get('transaction', [])
                    if transactions:
                        return transactions
                
                if attempt < self.max_retries - 1:
                    print(f"  ⏳ Попытка {attempt + 1}/{self.max_retries}: транзакций нет, повтор...")
                    time.sleep(self.retry_delay)
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        return []
    
    
    # ==================== СОХРАНЕНИЕ В БД ====================
    
    def save_account_to_db(self, account, client_id, bank_code):
        """Сохранить счет в БД"""
        try:
            # Парсим JSON поле 'account' для получения scheme_name, account_number, holder_name
            account_data = account.get('account', [])
            scheme_name = None
            account_number = None
            holder_name = None
            
            if account_data and len(account_data) > 0:
                acc = account_data[0]
                scheme_name = acc.get('schemeName')
                account_number = acc.get('identification')
                holder_name = acc.get('name')
            
            self.cursor.execute('''
                INSERT OR REPLACE INTO accounts
                (account_id, client_id, bank_code, status, currency,
                 account_type, account_subtype, nickname, opening_date,
                 scheme_name, account_number, account_holder_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                account.get('accountId'),
                client_id,
                bank_code,
                account.get('status'),
                account.get('currency'),
                account.get('accountType'),
                account.get('accountSubType'),
                account.get('nickname'),
                account.get('openingDate'),
                scheme_name,
                account_number,
                holder_name
            ))
            self.stats['accounts'] += 1
        except Exception as e:
            print(f"  ⚠️ Ошибка сохранения счета: {e}")
    
    
    def save_balance_to_db(self, balance, account_id, client_id, bank_code):
        """Сохранить баланс в БД (с заменой старых значений)"""
        try:
            amount_data = balance.get('amount', {})
            balance_type = balance.get('type')
            
            # Используем INSERT OR REPLACE для обновления существующих записей
            self.cursor.execute('''
                INSERT OR REPLACE INTO balances
                (account_id, client_id, bank_code, balance_type, amount, currency,
                date_time, credit_debit_indicator, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                account_id,
                client_id,
                bank_code,
                balance_type,
                amount_data.get('amount'),
                amount_data.get('currency'),
                balance.get('dateTime'),
                balance.get('creditDebitIndicator')
            ))
            self.stats['balances'] += 1
        except Exception as e:
            print(f"  ⚠️ Ошибка сохранения баланса: {e}")
    
    
    def save_transaction_to_db(self, transaction, account_id, client_id, bank_code):
        """Сохранить транзакцию в БД"""
        try:
            amount_data = transaction.get('amount', {})
            bank_tx_code = transaction.get('bankTransactionCode', {})
            
            transaction_id = transaction.get('transactionId')
            if not transaction_id:
                transaction_id = f"tx-{bank_code}-{int(time.time()*1000)}"
            
            self.cursor.execute('''
                INSERT OR IGNORE INTO transactions
                (transaction_id, account_id, client_id, bank_code, amount,
                 currency, credit_debit_indicator, status,
                 booking_date_time, value_date_time, transaction_code, transaction_information)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                transaction_id,
                account_id,
                client_id,
                bank_code,
                amount_data.get('amount'),
                amount_data.get('currency'),
                transaction.get('creditDebitIndicator'),
                transaction.get('status'),
                transaction.get('bookingDateTime'),
                transaction.get('valueDateTime'),
                bank_tx_code.get('code'),
                transaction.get('transactionInformation', '')
            ))
            self.stats['transactions'] += 1
        except Exception as e:
            print(f"  ⚠️ Ошибка сохранения транзакции: {e}")
    
    
    # ==================== ОСНОВНАЯ ЛОГИКА ====================
    
    def fetch_bank_data(self, bank):
        """Получить данные одного банка и сохранить в БД"""
        bank_name = bank['name']
        bank_code = bank['code']
        bank_url = bank['url']
        
        print(f"\n{'='*70}")
        print(f"🏦 БАНК: {bank_name} ({bank_code})")
        print(f"{'='*70}")
        
        # Сохраняем банк в БД
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO banks (code, name, url)
                VALUES (?, ?, ?)
            ''', (bank_code, bank_name, bank_url))
            self.stats['banks'] += 1
            self.conn.commit()
        except Exception as e:
            print(f"  ❌ Ошибка сохранения банка: {e}")
            return 0, 0
        
        # Получаем токен
        print(f"🔑 Получение токена...")
        token = self.get_token(bank_url)
        if not token:
            print(f"❌ Банк {bank_name} пропущен - нет токена\n")
            return 0, 0
        print(f"  ✅ Токен получен")
        
        # Получаем продукты
        print(f"📦 Получение продуктов...")
        products_count = self.get_products(bank_url, bank_code)
        print(f"  ✅ Получено {products_count} продуктов")
        
        # Получаем данные клиентов
        print(f"\n👥 Получение данных 10 клиентов...\n")
        successful_clients = 0
        failed_clients = []
        
        for i in range(1, 11):
            client_id = f"{self.client_id}-{i}"
            print(f"  👤 Клиент {i}/10: {client_id}")
            
            # Сохраняем клиента в БД
            try:
                self.cursor.execute('''
                    INSERT OR IGNORE INTO clients (client_id, bank_code)
                    VALUES (?, ?)
                ''', (client_id, bank_code))
                self.stats['clients'] += 1
                self.conn.commit()
            except Exception as e:
                print(f"  ❌ Ошибка сохранения клиента: {e}")
                failed_clients.append(client_id)
                continue
            
            # Получаем consent (используем существующий для vbank)
            consent_id = self.create_consent_with_retry(bank_url, token, client_id, bank_code)
            if not consent_id:
                print(f"  ❌ Согласие не получено")
                failed_clients.append(client_id)
                continue
            
            # Получаем счета
            accounts = self.get_accounts_with_retry(bank_url, token, client_id, consent_id)
            print(f"  → Счетов: {len(accounts)}")
            
            if not accounts:
                print(f"  ❌ Счета не получены после {self.max_retries} попыток")
                failed_clients.append(client_id)
                continue
            
            # Для каждого счета
            total_balances = 0
            total_transactions = 0
            
            for acc in accounts:
                acc_id = acc.get('accountId')
                
                # Сохраняем счет
                self.save_account_to_db(acc, client_id, bank_code)
                
                # Балансы
                balances = self.get_balances(bank_url, token, acc_id, consent_id)
                for bal in balances:
                    self.save_balance_to_db(bal, acc_id, client_id, bank_code)
                    total_balances += 1
                
                # Транзакции
                transactions = self.get_transactions_with_retry(bank_url, token, acc_id, consent_id)
                for tx in transactions:
                    self.save_transaction_to_db(tx, acc_id, client_id, bank_code)
                    total_transactions += 1
            
            # Сохраняем изменения после каждого клиента
            self.conn.commit()
            
            print(f"  💾 Балансов: {total_balances}, Транзакций: {total_transactions}")
            successful_clients += 1
            
            # Пауза между клиентами
            if i < 10:
                time.sleep(0.5)
        
        # Итоги по банку
        print(f"\n {'─'*66}")
        print(f"  ✅ Успешно: {successful_clients}/10 клиентов")
        if failed_clients:
            print(f"  ❌ Не удалось: {len(failed_clients)}")
            for client in failed_clients:
                print(f"    • {client}")
        print(f" {'─'*66}")
        
        return successful_clients, len(failed_clients)
    
    
    def fetch_all_banks(self):
        """Получить данные всех банков"""
        print("""
╔═══════════════════════════════════════════════════════════════════╗
║ 📊 ПРЯМОЙ ИМПОРТ ИЗ API БАНКОВ В SQLITE                         ║
║                                                                   ║
║ • Awesome Bank (abank) - 10 клиентов (auto)                     ║
║ • Virtual Bank (vbank) - 10 клиентов (existing consents)       ║
║                                                                   ║
║ БЕЗ промежуточного Excel файла                                   ║
╚═══════════════════════════════════════════════════════════════════╝
""")
        
        total_successful = 0
        total_failed = 0
        
        # Обрабатываем каждый банк
        for bank in self.banks:
            successful, failed = self.fetch_bank_data(bank)
            total_successful += successful
            total_failed += failed
            
            # Пауза между банками
            time.sleep(1)
        
        # Финальные итоги
        print(f"\n{'='*70}")
        print(f"🎉 ФИНАЛЬНЫЕ ИТОГИ ПО ВСЕМ БАНКАМ")
        print(f"{'='*70}")
        print(f"✅ Всего успешно обработано: {total_successful}/20 клиентов")
        print(f"❌ Не удалось обработать: {total_failed}/20 клиентов")
        print(f"{'='*70}\n")
        
        return total_successful > 0
    
    
    def print_statistics(self):
        """Вывести статистику БД"""
        print("\n" + "="*70)
        print("📊 СТАТИСТИКА БД:")
        print("="*70)
        
        # Общая статистика
        queries = [
            ('Банки', 'SELECT COUNT(*) FROM banks'),
            ('Клиенты', 'SELECT COUNT(*) FROM clients'),
            ('Счета', 'SELECT COUNT(*) FROM accounts'),
            ('Балансы', 'SELECT COUNT(*) FROM balances'),
            ('Транзакции', 'SELECT COUNT(*) FROM transactions'),
            ('Продукты', 'SELECT COUNT(*) FROM products'),
        ]
        
        print("\n  📈 Общая статистика:")
        for name, query in queries:
            count = self.cursor.execute(query).fetchone()[0]
            print(f"    {name}: {count}")
        
        # Детальная статистика по банкам
        print("\n  📊 По банкам:")
        all_banks = self.cursor.execute('SELECT code, name FROM banks ORDER BY code').fetchall()
        
        for bank_code, bank_name in all_banks:
            print(f"\n    {bank_name} ({bank_code}):")
            
            clients = self.cursor.execute(
                'SELECT COUNT(*) FROM clients WHERE bank_code = ?',
                (bank_code,)
            ).fetchone()[0] or 0
            
            accounts = self.cursor.execute(
                'SELECT COUNT(*) FROM accounts WHERE bank_code = ?',
                (bank_code,)
            ).fetchone()[0] or 0
            
            transactions = self.cursor.execute(
                'SELECT COUNT(*) FROM transactions WHERE bank_code = ?',
                (bank_code,)
            ).fetchone()[0] or 0
            
            balances = self.cursor.execute(
                'SELECT COUNT(*) FROM balances WHERE bank_code = ?',
                (bank_code,)
            ).fetchone()[0] or 0
            
            products = self.cursor.execute(
                'SELECT COUNT(*) FROM products WHERE bank_code = ?',
                (bank_code,)
            ).fetchone()[0] or 0
            
            print(f"      • Клиентов: {clients}")
            print(f"      • Счетов: {accounts}")
            print(f"      • Балансов: {balances}")
            print(f"      • Транзакций: {transactions}")
            print(f"      • Продуктов: {products}")
        
        print("="*70)
    
    
    def close(self):
        """Закрыть соединение с БД"""
        if self.conn:
            self.conn.close()
    
    
    def run(self):
        """Запустить полный процесс"""
        try:
            # Создаем БД
            self.create_database()
            
            # Получаем данные из всех банков
            if self.fetch_all_banks():
                # Выводим статистику
                self.print_statistics()
                print(f"\n✅ Готово! База данных создана: {self.db_file}")
                return True
            else:
                print("\n❌ Не удалось получить данные ни из одного банка")
                return False
                
        except Exception as e:
            print(f"\n❌ Критическая ошибка: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.close()


def main():
    """Главная функция"""
    importer = DirectAPIToSQLite('multibank_real.db')
    importer.run()


if __name__ == "__main__":
    main()
