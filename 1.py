#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ChatGPT Registration Bot
Полная версия с улучшенным заполнением даты
"""

import time
import random
import string
import os
import imaplib
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

# Списки для генерации имени
FIRST_NAMES = ["John", "James", "Robert", "Michael", "William", "David", "Richard", "Thomas", "Charles", "Daniel"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
# =====================================================

def generate_full_name():
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    return f"{first} {last}"

def generate_birth_date():
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    year = random.randint(1970, 2005)
    return f"{month:02d}/{day:02d}/{year}"

def human_type(element, text, delay_min=0.05, delay_max=0.15):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(delay_min, delay_max))

def get_verification_code(email, password, timeout=120):
    try:
        print(f"[*] Подключаюсь к IMAP...")
        mail = imaplib.IMAP4_SSL(FIRSTMAIL_IMAP, FIRSTMAIL_IMAP_PORT)
        mail.login(email, password)
        mail.select('inbox')
        
        start_time = time.time()
        last_count = 0
        
        while time.time() - start_time < timeout:
            result, data = mail.search(None, 'ALL')
            if result == 'OK':
                uids = data[0].split()
                current_count = len(uids)
                
                if current_count > last_count:
                    print(f"[*] Новое письмо! Всего: {current_count}")
                    last_count = current_count
                    
                    latest = uids[-1]
                    result, msg_data = mail.fetch(latest, '(RFC822)')
                    
                    if result == 'OK':
                        raw_email = msg_data[0][1]
                        if isinstance(raw_email, bytes):
                            msg_str = raw_email.decode('utf-8', errors='ignore')
                        else:
                            msg_str = str(raw_email)
                        
                        match = re.search(r'\b(\d{6})\b', msg_str)
                        if match:
                            code = match.group(1)
                            print(f"[+] Код: {code}")
                            mail.close()
                            mail.logout()
                            return code
                else:
                    print(f"[*] Жду письмо... ({current_count} писем)")
            
            time.sleep(5)
        
        mail.close()
        mail.logout()
        
    except Exception as e:
        print(f"[!] Ошибка IMAP: {e}")
    
    return None

def find_field_by_label(sb, label_text, timeout=5):
    try:
        xpath = f"//label[contains(text(), '{label_text}')]"
        label = sb.find_element(xpath, timeout=timeout)
        if label:
            for_id = label.get_attribute("for")
            if for_id:
                try:
                    return sb.find_element(f"#{for_id}", timeout=2)
                except:
                    pass
    except:
        pass
    return None

def find_field_by_placeholder(sb, placeholder_text, timeout=5):
    try:
        return sb.find_element(f"input[placeholder*='{placeholder_text}']", timeout=timeout)
    except:
        pass
    return None

def find_password_field(sb, timeout=10):
    # Ищем поле пароля
    try:
        field = sb.find_element("input[type='password']", timeout=timeout)
        if field:
            return field
    except:
        pass
    
    try:
        field = sb.find_element("input[name*='password']", timeout=timeout)
        if field:
            return field
    except:
        pass
    
    return None

def fill_date_field(sb, birth_date):
    """Заполняет поле даты рождения (улучшенная версия)"""
    print(f"[*] Заполняю дату: {birth_date}")
    
    # Способ 1: Ищем сегменты даты
    try:
        segments = sb.find_elements("[data-rac-data-type]")
        if len(segments) >= 3:
            month, day, year = birth_date.split('/')
            
            for i, seg in enumerate(segments[:3]):
                try:
                    sb.execute_script("arguments[0].click();", seg)
                    time.sleep(0.3)
                    if i == 0:
                        human_type(seg, month)
                    elif i == 1:
                        human_type(seg, day)
                    else:
                        human_type(seg, year)
                    time.sleep(0.3)
                except Exception as e:
                    print(f"[-] Ошибка при вводе сегмента {i}: {e}")
                    pass
            
            print("[✓] Дата заполнена через сегменты")
            return True
    except:
        pass
    
    # Способ 2: Ищем input type="date"
    try:
        date_field = sb.find_element("input[type='date']", timeout=3)
        if date_field:
            date_field.click()
            time.sleep(0.2)
            try:
                date_field.clear()
            except:
                pass
            date_field.send_keys(birth_date.replace('/', ''))
            print("[✓] Дата заполнена через input date")
            return True
    except:
        pass
    
    # Способ 3: Ищем по лейблу
    try:
        labels = ["Birthday", "Date of birth", "Birth date", "Дата рождения"]
        for label_text in labels:
            field = find_field_by_label(sb, label_text, 2)
            if field:
                field.click()
                time.sleep(0.2)
                try:
                    field.clear()
                except:
                    pass
                human_type(field, birth_date)
                print(f"[✓] Дата заполнена через лейбл: {label_text}")
                return True
    except:
        pass
    
    # Способ 4: Ищем по placeholder
    try:
        placeholders = ["birth", "date", "дд/мм/гггг", "mm/dd/yyyy", "MM/DD/YYYY"]
        for ph in placeholders:
            field = find_field_by_placeholder(sb, ph, 2)
            if field:
                field.click()
                time.sleep(0.2)
                try:
                    field.clear()
                except:
                    pass
                clean_date = birth_date.replace('/', '')
                human_type(field, clean_date)
                print(f"[✓] Дата заполнена через placeholder: {ph}")
                return True
    except:
        pass
    
    # Способ 5 (Резервный): Ищем по имени поля 'birthday' или id
    try:
        field = sb.find_element("input[name*='birth'], input[id*='birth']", timeout=2)
        if field:
            field.click()
            time.sleep(0.2)
            clean_date = birth_date.replace('/', '')
            human_type(field, clean_date)
            print("[✓] Дата заполнена через резервный поиск")
            return True
    except:
        pass
    
    print("[!] Поле даты не найдено")
    return False

def register_chatgpt(email, email_password):
    chatgpt_password = FIXED_PASSWORD
    full_name = generate_full_name()
    birth_date = generate_birth_date()
    
    print(f"\n{'='*50}")
    print(f"[*] Почта: {email}")
    print(f"[*] Пароль ChatGPT: {chatgpt_password}")
    print(f"[*] Имя: {full_name}")
    print(f"[*] Дата: {birth_date}")
    print(f"{'='*50}")
    
    with SB(uc=True, headless=False) as sb:
        
        # 1. Открытие
        print("\n[1] Открытие ChatGPT...")
        sb.uc_open_with_reconnect("https://chatgpt.com", 20)
        time.sleep(DELAY_STEP)
        
        # 2. Sign up
        print("\n[2] Нажатие Sign up...")
        try:
            sb.click("button[data-testid='signup-button']", timeout=10)
        except:
            sb.click("//button[contains(text(), 'Sign up')]", timeout=10)
        time.sleep(DELAY_STEP)
        
        # 3. Email
        print("\n[3] Ввод email...")
        email_field = sb.find_element("input[type='email']", timeout=10)
        if email_field:
            human_type(email_field, email)
            print(f"[✓] Email: {email}")
        else:
            return False
        time.sleep(DELAY_STEP)
        
        # 4. Continue
        print("\n[4] Continue...")
        sb.click("button[type='submit']")
        time.sleep(DELAY_STEP)
        
        # 5. Пароль
        print("\n[5] Ввод пароля...")
        password_field = find_password_field(sb, timeout=10)
        if not password_field:
            return False
        human_type(password_field, chatgpt_password)
        print(f"[✓] Пароль: {chatgpt_password}")
        time.sleep(DELAY_STEP)
        
        # 6. Continue
        print("\n[6] Continue...")
        sb.click("button[type='submit']")
        time.sleep(DELAY_STEP)
        
        # 7. Ожидание кода
        print("\n[7] Ожидание кода...")
        try:
            sb.wait_for_element_visible("input[name='code']", timeout=30)
            print("[✓] Поле кода появилось")
        except:
            return False
        
        # 8. Получение кода
        print("\n[8] Получение кода...")
        code = get_verification_code(email, email_password, timeout=120)
        if not code:
            return False
        
        # 9. Ввод кода
        print(f"\n[9] Ввод кода: {code}")
        code_field = sb.find_element("input[name='code']")
        human_type(code_field, code)
        time.sleep(DELAY_STEP)
        
        # 10. Continue
        print("\n[10] Continue...")
        sb.click("button[type='submit']")
        time.sleep(DELAY_STEP)
        
        # 11. Имя
        print("\n[11] Ввод имени...")
        name_field = None
        try:
            name_field = sb.find_element("input[name='first_name']", timeout=5)
        except:
            try:
                name_field = sb.find_element("input[name='name']", timeout=5)
            except:
                pass
        
        if name_field:
            human_type(name_field, full_name)
            print(f"[✓] Имя: {full_name}")
        else:
            print("[!] Поле имени не найдено")
        
        time.sleep(DELAY_STEP)
        
        # 12. Дата рождения
        print("\n[12] Ввод даты рождения...")
        fill_date_field(sb, birth_date)
        time.sleep(DELAY_STEP)
        
        # 13. Continue
        print("\n[13] Continue...")
        try:
            sb.click("button[type='submit']")
            print("[✓] Continue нажата")
        except:
            print("[!] Кнопка Continue не найдена")
        
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
    print("Улучшенное заполнение даты (5 способов)")
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
