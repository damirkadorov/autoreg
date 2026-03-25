#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ChatGPT Auto-Registrator
Получение кода через IMAP (Firstmail)
"""

import time
import random
import string
import os
import imaplib
import email
import re

from seleniumbase import SB

# ===================== НАСТРОЙКИ =====================
EMAILS_FILE = "emails.txt"
OUTPUT_FILE = "chatgpt_accounts.txt"
DELAY_STEP = 3
FIXED_PASSWORD = "Mudakiv12345@"
FULL_NAME = "John Smith"
BIRTH_DATE = "01/01/2000"

# IMAP настройки для Firstmail
FIRSTMAIL_IMAP = "imap.firstmail.ltd"
FIRSTMAIL_IMAP_PORT = 993
# =====================================================

def human_type(element, text, delay_min=0.08, delay_max=0.2):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(delay_min, delay_max))

def get_verification_code_imap(email, password, timeout=120):
    """Получает код подтверждения через IMAP Firstmail"""
    
    print(f"[*] Подключение к IMAP: {FIRSTMAIL_IMAP}:{FIRSTMAIL_IMAP_PORT}")
    
    try:
        mail = imaplib.IMAP4_SSL(FIRSTMAIL_IMAP, FIRSTMAIL_IMAP_PORT)
        mail.login(email, password)
        mail.select('inbox')
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            print(f"[*] Проверка писем для {email}...")
            
            # Ищем письма от OpenAI
            result, data = mail.search(None, '(FROM "openai.com" OR FROM "tm.openai.com")')
            
            if result == 'OK' and data[0]:
                email_ids = data[0].split()
                if email_ids:
                    # Берём последнее письмо
                    latest_id = email_ids[-1]
                    result, msg_data = mail.fetch(latest_id, '(RFC822)')
                    
                    msg = email.message_from_bytes(msg_data[0][1])
                    
                    # Извлекаем тело письма
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                payload = part.get_payload(decode=True)
                                body = payload.decode('utf-8', errors='ignore')
                                break
                    else:
                        payload = msg.get_payload(decode=True)
                        body = payload.decode('utf-8', errors='ignore')
                    
                    print(f"[DEBUG] Тело письма: {body[:200]}...")
                    
                    # Ищем 6-значный код
                    match = re.search(r'\b(\d{6})\b', body)
                    if match:
                        code = match.group(1)
                        print(f"[+] Код найден: {code}")
                        mail.close()
                        mail.logout()
                        return code
                    else:
                        print("[*] Код в письме не найден, ждём новое...")
            
            time.sleep(5)
        
        mail.close()
        mail.logout()
        
    except Exception as e:
        print(f"[!] Ошибка IMAP: {e}")
        return None
    
    print(f"[-] Код не получен за {timeout} сек")
    return None

def register_chatgpt(email, email_password):
    chatgpt_password = FIXED_PASSWORD
    
    print(f"\n{'='*50}")
    print(f"[*] Почта: {email}")
    print(f"[*] Пароль от почты: {email_password}")
    print(f"[*] Пароль ChatGPT: {chatgpt_password}")
    print(f"{'='*50}")
    
    with SB(uc=True, headless=False) as sb:
        
        # ========== ЭТАП 1: Открытие ChatGPT ==========
        print("\n--- ЭТАП 1: Открытие ChatGPT (3 сек) ---")
        sb.uc_open_with_reconnect("https://chatgpt.com", 20)
        time.sleep(DELAY_STEP)
        
        # ========== ЭТАП 2: Нажатие "Sign up" ==========
        print("\n--- ЭТАП 2: Нажатие Sign up (3 сек) ---")
        try:
            sb.click("button[data-testid='signup-button']", timeout=10)
        except:
            sb.click("//button[contains(text(), 'Sign up')]", timeout=10)
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
        
        # ========== ЭТАП 5: Ввод Full Name ==========
        print("\n--- ЭТАП 5: Ввод Full Name (3 сек) ---")
        name_field = None
        for selector in ["input[name='first_name']", "input[name='name']", "input[placeholder*='Name']"]:
            try:
                name_field = sb.find_element(selector, timeout=3)
                if name_field and name_field.is_displayed():
                    print(f"[✓] Найдено поле: {selector}")
                    break
            except:
                continue
        
        if name_field:
            human_type(name_field, FULL_NAME)
            print(f"[✓] Имя введено: {FULL_NAME}")
        else:
            print("[!] Поле имени не найдено")
        
        time.sleep(DELAY_STEP)
        
        # ========== ЭТАП 6: Нажатие Continue ==========
        print("\n--- ЭТАП 6: Нажатие Continue (3 сек) ---")
        try:
            sb.click("button[type='submit']")
        except:
            pass
        time.sleep(DELAY_STEP)
        
        # ========== ЭТАП 7: Ввод даты рождения ==========
        print("\n--- ЭТАП 7: Ввод даты рождения (3 сек) ---")
        date_field = None
        for selector in ["input[name='birth_date']", "input[placeholder*='birth']", "input[type='date']"]:
            try:
                date_field = sb.find_element(selector, timeout=3)
                if date_field and date_field.is_displayed():
                    print(f"[✓] Найдено поле: {selector}")
                    break
            except:
                continue
        
        if date_field:
            human_type(date_field, BIRTH_DATE)
            print(f"[✓] Дата рождения введена: {BIRTH_DATE}")
        else:
            print("[!] Поле даты рождения не найдено")
        
        time.sleep(DELAY_STEP)
        
        # ========== ЭТАП 8: Нажатие Continue ==========
        print("\n--- ЭТАП 8: Нажатие Continue (3 сек) ---")
        try:
            sb.click("button[type='submit']")
        except:
            pass
        time.sleep(DELAY_STEP)
        
        # ========== ЭТАП 9: Ввод пароля ==========
        print("\n--- ЭТАП 9: Ввод пароля (3 сек) ---")
        password_field = None
        for selector in ["input[name='password']", "input[type='password']", "input[placeholder='Password']"]:
            try:
                password_field = sb.find_element(selector, timeout=5)
                if password_field and password_field.is_displayed():
                    print(f"[✓] Найдено поле: {selector}")
                    break
            except:
                continue
        
        if not password_field:
            print("[-] Поле пароля не найдено")
            return False
        
        human_type(password_field, chatgpt_password)
        print(f"[✓] Пароль введён: {chatgpt_password}")
        time.sleep(DELAY_STEP)
        
        # ========== ЭТАП 10: Нажатие Continue после пароля ==========
        print("\n--- ЭТАП 10: Нажатие Continue (3 сек) ---")
        sb.click("button[type='submit']")
        time.sleep(DELAY_STEP)
        
        # ========== ЭТАП 11: Ожидание кода ==========
        print("\n--- ЭТАП 11: Ожидание кода подтверждения ---")
        
        # Ждём поле для кода
        try:
            sb.wait_for_element_visible("input[name='code']", timeout=30)
            print("[✓] Поле для кода появилось")
        except:
            print("[-] Поле для кода не появилось")
            return False
        
        # Получаем код через IMAP
        code = get_verification_code_imap(email, email_password, timeout=120)
        if not code:
            print("[-] Не удалось получить код")
            return False
        
        # ========== ЭТАП 12: Ввод кода ==========
        print(f"\n--- ЭТАП 12: Ввод кода {code} (3 сек) ---")
        code_field = sb.find_element("input[name='code']")
        human_type(code_field, code)
        time.sleep(DELAY_STEP)
        
        # ========== ЭТАП 13: Нажатие Continue после кода ==========
        print("\n--- ЭТАП 13: Нажатие Continue (3 сек) ---")
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
    print(f"IMAP сервер: {FIRSTMAIL_IMAP}:{FIRSTMAIL_IMAP_PORT}")
    print("=" * 60)
    
    emails = load_emails()
    if not emails:
        return
    
    print("\n⚠️ ПОРЯДОК ДЕЙСТВИЙ:")
    print("   1. Cloudflare обходится автоматически")
    print("   2. Email → Continue")
    print("   3. Full Name → Continue")
    print("   4. Дата рождения → Continue")
    print(f"   5. Пароль {FIXED_PASSWORD} → Continue")
    print("   6. Код из почты (IMAP) → Continue")
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
