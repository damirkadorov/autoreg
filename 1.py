#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ChatGPT Auto-Registrator
Правильный порядок: email → пароль → код
"""

import time
import random
import string
import os
import requests
import re

from seleniumbase import SB

# ===================== НАСТРОЙКИ =====================
EMAILS_FILE = "emails.txt"
OUTPUT_FILE = "chatgpt_accounts.txt"
FIRSTMAIL_API = "https://firstmail.ltd/api/v1/email/messages"
FIRSTMAIL_TOKEN = "kv3wxML6Ibxo2ok1SPJCVonQIM09TWDgqjf0_S3BcVWIfvZVx9XlqcioEKn6qiXt"
DELAY_STEP = 3
FIXED_PASSWORD = "Mudakiv12345@"
# =====================================================

def human_type(element, text, delay_min=0.08, delay_max=0.2):
    """Имитирует печать как на клавиатуре"""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(delay_min, delay_max))

def get_verification_code(email, password, timeout=120):
    headers = {
        "Authorization": f"Bearer {FIRSTMAIL_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "email": email,
        "password": password,
        "limit": 10,
        "folder": "INBOX"
    }
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        print(f"[*] Проверка писем для {email}...")
        try:
            response = requests.post(FIRSTMAIL_API, headers=headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    messages = data.get('data', {}).get('messages', [])
                    for msg in messages:
                        from_addr = msg.get('from', [])
                        from_str = str(from_addr[0]) if isinstance(from_addr, list) else str(from_addr)
                        if "openai.com" in from_str or "tm.openai.com" in from_str:
                            subject = msg.get('subject', '')
                            body = msg.get('body', '')
                            full_text = subject + " " + body
                            match = re.search(r'\b(\d{6})\b', full_text)
                            if match:
                                print(f"[+] Код найден: {match.group(1)}")
                                return match.group(1)
            time.sleep(5)
        except Exception as e:
            print(f"[!] Ошибка API: {e}")
            time.sleep(5)
    
    print(f"[-] Код не получен за {timeout} сек")
    return None

def find_password_field(sb, timeout=10):
    """Ищет поле пароля по тексту лейбла или плейсхолдеру"""
    
    # Способ 1: Ищем лейбл с текстом "Password"
    try:
        label = sb.find_element("//label[contains(text(), 'Password')]", timeout=timeout)
        if label:
            for_id = label.get_attribute("for")
            if for_id:
                field = sb.find_element(f"#{for_id}", timeout=3)
                if field:
                    print("[✓] Поле пароля найдено через лейбл (for)")
                    return field
            field = sb.find_element(".//following-sibling::input", timeout=3)
            if field:
                print("[✓] Поле пароля найдено через лейбл (сосед)")
                return field
    except:
        pass
    
    # Способ 2: Ищем input с placeholder "Password"
    try:
        field = sb.find_element("input[placeholder='Password']", timeout=timeout)
        if field:
            print("[✓] Поле пароля найдено через placeholder")
            return field
    except:
        pass
    
    # Способ 3: Ищем input type="password"
    try:
        fields = sb.find_elements("input[type='password']")
        for field in fields:
            if field.is_displayed():
                print("[✓] Поле пароля найдено через type='password'")
                return field
    except:
        pass
    
    print("[-] Поле пароля не найдено")
    return None

def register_chatgpt(email, email_password):
    chatgpt_password = FIXED_PASSWORD
    
    print(f"\n{'='*50}")
    print(f"[*] Почта: {email}")
    print(f"[*] Пароль ChatGPT: {chatgpt_password}")
    print(f"{'='*50}")
    
    with SB(uc=True, headless=False) as sb:
        
        # ========== ЭТАП 1: Открытие ChatGPT ==========
        print("\n--- ЭТАП 1: Открытие ChatGPT (3 сек) ---")
        sb.uc_open_with_reconnect("https://chatgpt.com", 20)
        time.sleep(DELAY_STEP)
        
        # ========== ЭТАП 2: Нажатие "Log in" ==========
        print("\n--- ЭТАП 2: Нажатие Log in (3 сек) ---")
        try:
            sb.click("button[data-testid='login-button']", timeout=10)
        except:
            sb.click("//button[contains(text(), 'Log in')]", timeout=10)
        time.sleep(DELAY_STEP)
        
        # ========== ЭТАП 3: Ввод email ==========
        print("\n--- ЭТАП 3: Ввод email (3 сек) ---")
        email_field = sb.find_element("input[name='email']")
        human_type(email_field, email)
        print(f"[✓] Email введён: {email}")
        time.sleep(DELAY_STEP)
        
        # ========== ЭТАП 4: Нажатие Continue ==========
        print("\n--- ЭТАП 4: Нажатие Continue (3 сек) ---")
        sb.click("button[type='submit']")
        time.sleep(DELAY_STEP)
        
        # ========== ЭТАП 5: Ввод пароля ==========
        print("\n--- ЭТАП 5: Поиск поля пароля и ввод (3 сек) ---")
        
        password_field = find_password_field(sb, timeout=10)
        if not password_field:
            print("[-] Поле пароля не найдено")
            return False
        
        human_type(password_field, chatgpt_password)
        print(f"[✓] Пароль введён: {chatgpt_password}")
        time.sleep(DELAY_STEP)
        
        # ========== ЭТАП 6: Нажатие Continue после пароля ==========
        print("\n--- ЭТАП 6: Нажатие Continue (3 сек) ---")
        sb.click("button[type='submit']")
        time.sleep(DELAY_STEP)
        
        # ========== ЭТАП 7: Ожидание кода ==========
        print("\n--- ЭТАП 7: Ожидание кода подтверждения ---")
        
        # Ждём поле для кода
        try:
            sb.wait_for_element_visible("input[name='code']", timeout=30)
            print("[✓] Поле для кода появилось")
        except:
            print("[-] Поле для кода не появилось")
            return False
        
        # Получаем код из почты
        code = get_verification_code(email, email_password, timeout=120)
        if not code:
            print("[-] Не удалось получить код")
            return False
        
        # ========== ЭТАП 8: Ввод кода ==========
        print(f"\n--- ЭТАП 8: Ввод кода {code} (3 сек) ---")
        code_field = sb.find_element("input[name='code']")
        human_type(code_field, code)
        time.sleep(DELAY_STEP)
        
        # ========== ЭТАП 9: Нажатие Continue после кода ==========
        print("\n--- ЭТАП 9: Нажатие Continue (3 сек) ---")
        sb.click("button[type='submit']")
        time.sleep(DELAY_STEP)
        
        # ========== СОХРАНЕНИЕ ==========
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{email}:{chatgpt_password}\n")
        
        print(f"\n[+] Аккаунт ChatGPT сохранён: {email}")
        return True

def load_emails():
    emails = []
    try:
        with open(EMAILS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and ':' in line:
                    email, pwd = line.split(':', 1)
                    emails.append((email, pwd))
        print(f"[+] Загружено {len(emails)} почтовых аккаунтов")
    except FileNotFoundError:
        print(f"[-] Файл {EMAILS_FILE} не найден!")
        return []
    return emails

def main():
    print("=" * 60)
    print("ChatGPT Auto-Registrator")
    print(f"Фиксированный пароль: {FIXED_PASSWORD}")
    print("Правильный порядок: email → пароль → код")
    print("Реалистичная печать как на клавиатуре")
    print(f"Пауза между этапами: {DELAY_STEP} секунд")
    print("=" * 60)
    
    emails = load_emails()
    if not emails:
        return
    
    print("\n⚠️ ПОРЯДОК ДЕЙСТВИЙ:")
    print("   1. Cloudflare обходится автоматически")
    print("   2. Email → Continue")
    print(f"   3. Пароль {FIXED_PASSWORD} → Continue")
    print("   4. Код из почты → Continue")
    print("=" * 60)
    
    try:
        count = int(input("\nСколько аккаунтов создать: ") or len(emails))
        count = min(count, len(emails))
    except:
        count = len(emails)
    
    success = 0
    for i in range(count):
        email, email_password = emails[i]
        print(f"\n{'#'*50}")
        print(f"Аккаунт {i+1}/{count}")
        print(f"{'#'*50}")
        
        if register_chatgpt(email, email_password):
            success += 1
        else:
            print(f"[-] Аккаунт {i+1} не создан")
        
        if i < count - 1:
            print("\n[*] Ожидание 10 секунд...")
            time.sleep(10)
    
    print("\n" + "=" * 60)
    print(f"✅ Создано: {success}/{count}")
    print(f"📁 Файл: {OUTPUT_FILE}")
    print("=" * 60)

if __name__ == "__main__":
    main()
