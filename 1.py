#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mail.ee Auto-Registrator
Простая версия с SeleniumBase
"""

import time
import random
import string
import os

from seleniumbase import SB

# ===================== НАСТРОЙКИ =====================
OUTPUT_FILE = "mail_ee_accounts.txt"
# =====================================================

FIRST_NAMES = ["mari", "juri", "anna", "kristi", "tarmo", "liisa", "janek", "kadri", "rain", "silja", "marten", "merle", "andres", "triin", "priit"]
LAST_NAMES = ["jari", "tamm", "saar", "kask", "sepp", "mets", "pärn", "rebase", "ojamaa", "kallas", "mägi", "rand", "veski", "laur", "villems"]

def generate_username():
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    year = random.randint(1950, 2005)
    return f"{first}{last}{year}".lower()

def generate_password():
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=12))

def register():
    username = generate_username()
    password = generate_password()
    email = f"{username}@mail.ee"
    
    print(f"\n[*] Регистрация: {email}")
    print(f"[*] Пароль: {password}")
    
    with SB(uc=True, headless=False) as sb:
        
        # Открыть страницу
        sb.uc_open_with_reconnect("https://login.mail.ee/signup?go=portal", 15)
        time.sleep(3)
        
        # Куки
        try:
            sb.click("#accept-btn", timeout=5)
            print("[✓] Куки приняты")
        except:
            pass
        time.sleep(2)
        
        # Имя
        sb.type("#signup_user", username)
        print(f"[✓] Имя: {username}")
        time.sleep(2)
        
        # Проверить имя
        sb.click("#check-uname")
        print("[✓] Проверка имени")
        time.sleep(3)
        
        # Пароль
        sb.type("input[name='password']", password)
        print("[✓] Пароль")
        time.sleep(2)
        
        # Галочки
        for cb in sb.find_elements("//input[@type='checkbox']"):
            if not cb.is_selected():
                cb.click()
                time.sleep(1)
        
        # Создать аккаунт
        sb.click("//button[contains(text(), 'Loo uus konto')]")
        print("[✓] Создание аккаунта")
        time.sleep(3)
        
        # hCaptcha (вручную)
        print("\n🔐 РЕШИТЕ hCaptcha ВРУЧНУЮ")
        input("Нажмите Enter после решения капчи...")
        
        # Сохранить
        with open(OUTPUT_FILE, 'a') as f:
            f.write(f"{email}:{password}\n")
        
        print(f"[+] Сохранён: {email}")
        return True

def main():
    print("=" * 50)
    print("Mail.ee Generator (SeleniumBase)")
    print("=" * 50)
    
    if "DISPLAY" not in os.environ:
        os.environ["DISPLAY"] = ":0"
    
    count = int(input("\nСколько аккаунтов: ") or 1)
    
    for i in range(count):
        print(f"\n--- {i+1}/{count} ---")
        register()
        if i < count - 1:
            time.sleep(10)
    
    print(f"\n✅ Готово! Файл: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
