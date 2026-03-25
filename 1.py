#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ChatGPT Registration Bot
Полная автоматическая регистрация ChatGPT
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

# IMAP для Firstmail
FIRSTMAIL_IMAP = "imap.firstmail.ltd"
FIRSTMAIL_IMAP_PORT = 993
# =====================================================

def human_type(element, text, delay_min=0.05, delay_max=0.15):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(delay_min, delay_max))

def get_verification_code(email, password, timeout=120):
    """Получает код подтверждения через IMAP Firstmail"""
    try:
        mail = imaplib.IMAP4_SSL(FIRSTMAIL_IMAP, FIRSTMAIL_IMAP_PORT)
        mail.login(email, password)
        mail.select('inbox')
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            print(f"[*] Проверка писем...")
            result, data = mail.search(None, '(FROM "openai.com" OR FROM "tm.openai.com")')
            
            if result == 'OK' and data[0]:
                email_ids = data[0].split()
                if email_ids:
                    latest_id = email_ids[-1]
                    result, msg_data = mail.fetch(latest_id, '(RFC822)')
                    msg = email.message_from_bytes(msg_data[0][1])
                    
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
                    
                    match = re.search(r'\b(\d{6})\b', body)
                    if match:
                        code = match.group(1)
                        print(f"[+] Код: {code}")
                        mail.close()
                        mail.logout()
                        return code
            
            time.sleep(5)
        
        mail.close()
        mail.logout()
        
    except Exception as e:
        print(f"[!] Ошибка IMAP: {e}")
    
    return None

def register_chatgpt(email, email_password):
    chatgpt_password = FIXED_PASSWORD
    
    print(f"\n{'='*50}")
    print(f"[*] Почта: {email}")
    print(f"[*] Пароль ChatGPT: {chatgpt_password}")
    print(f"{'='*50}")
    
    with SB(uc=True, headless=False) as sb:
        
        # 1. Открытие ChatGPT
        print("\n[1] Открытие ChatGPT...")
        sb.uc_open_with_reconnect("https://chatgpt.com", 20)
        time.sleep(DELAY_STEP)
        
        # 2. Нажатие Sign up
        print("\n[2] Нажатие Sign up...")
        try:
            sb.click("button[data-testid='signup-button']", timeout=10)
        except:
            sb.click("//button[contains(text(), 'Sign up')]", timeout=10)
        time.sleep(DELAY_STEP)
        
        # 3. Ввод email
        print("\n[3] Ввод email...")
        email_field = sb.find_element("input[name='email']")
        human_type(email_field, email)
        time.sleep(DELAY_STEP)
        
        # 4. Continue
        print("\n[4] Continue...")
        sb.click("button[type='submit']")
        time.sleep(DELAY_STEP)
        
        # 5. Ввод имени (если есть)
        print("\n[5] Проверка поля имени...")
        try:
            name_field = sb.find_element("input[name='first_name']", timeout=3)
            if name_field and name_field.is_displayed():
                human_type(name_field, "John Smith")
                print("[✓] Имя введено")
                time.sleep(DELAY_STEP)
                sb.click("button[type='submit']")
                time.sleep(DELAY_STEP)
        except:
            pass
        
        # 6. Ввод даты рождения (если есть)
        print("\n[6] Проверка поля даты...")
        try:
            date_field = sb.find_element("input[type='date']", timeout=3)
            if date_field and date_field.is_displayed():
                human_type(date_field, "2000-01-01")
                print("[✓] Дата введена")
                time.sleep(DELAY_STEP)
                sb.click("button[type='submit']")
                time.sleep(DELAY_STEP)
        except:
            pass
        
        # 7. Ввод пароля
        print("\n[7] Ввод пароля...")
        password_field = sb.find_element("input[name='password']")
        human_type(password_field, chatgpt_password)
        time.sleep(DELAY_STEP)
        
        # 8. Continue
        print("\n[8] Continue...")
        sb.click("button[type='submit']")
        time.sleep(DELAY_STEP)
        
        # 9. Ожидание поля для кода
        print("\n[9] Ожидание кода...")
        try:
            sb.wait_for_element_visible("input[name='code']", timeout=30)
            print("[✓] Поле кода появилось")
        except:
            print("[-] Поле кода не появилось")
            return False
        
        # 10. Получение кода из почты
        print("\n[10] Получение кода...")
        code = get_verification_code(email, email_password, timeout=120)
        if not code:
            return False
        
        # 11. Ввод кода
        print(f"\n[11] Ввод кода: {code}")
        code_field = sb.find_element("input[name='code']")
        human_type(code_field, code)
        time.sleep(DELAY_STEP)
        
        # 12. Continue
        print("\n[12] Continue...")
        sb.click("button[type='submit']")
        time.sleep(DELAY_STEP)
        
        # Сохранение
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{email}:{chatgpt_password}\n")
        
        print(f"\n[+] Аккаунт сохранён: {email}")
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
        print(f"[+] Загружено {len(emails)} аккаунтов")
    except FileNotFoundError:
        print(f"[-] Файл {EMAILS_FILE} не найден!")
    return emails

def main():
    print("=" * 60)
    print("ChatGPT Registration Bot")
    print(f"Пароль: {FIXED_PASSWORD}")
    print(f"IMAP: {FIRSTMAIL_IMAP}:{FIRSTMAIL_IMAP_PORT}")
    print("=" * 60)
    
    emails = load_emails()
    if not emails:
        return
    
    count = int(input("\nСколько аккаунтов создать: ") or len(emails))
    count = min(count, len(emails))
    
    success = 0
    for i in range(count):
        email, email_password = emails[i]
        print(f"\n{'#'*50}")
        print(f"Аккаунт {i+1}/{count}")
        print(f"{'#'*50}")
        
        if register_chatgpt(email, email_password):
            success += 1
        else:
            print(f"[-] Ошибка")
        
        if i < count - 1:
            print("\n[*] Ожидание 10 сек...")
            time.sleep(10)
    
    print(f"\n✅ Готово: {success}/{count}")
    print(f"📁 Файл: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
