#!/usr/bin/env python3
"""
Скрипт для генерации хеша пароля
Использовать для создания безопасного хеша для .env файла
"""

import bcrypt

def generate_hash(password: str) -> str:
    """Генерирует bcrypt хеш для пароля"""
    # Генерируем соль и хеш
    salt = bcrypt.gensalt(rounds=12)  # 12 раундов = хороший баланс безопасности/скорости
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

if __name__ == '__main__':
    print("=== Генератор хешей паролей ===\n")
    
    password = input("Введите пароль для хеширования: ")
    
    if len(password) < 8:
        print("⚠️ Предупреждение: пароль слишком короткий (минимум 8 символов)")
    
    hashed = generate_hash(password)
    
    print("\n✅ Хеш сгенерирован:")
    print(hashed)
    print("\nДобавьте этот хеш в .env файл:")
    print(f'AUTH_PASSWORD_HASH={hashed}')
