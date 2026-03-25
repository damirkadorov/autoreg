#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mail.ee Auto-Registrator с SeleniumBase
Правильный селектор для кнопки куки: id="accept-btn"
"""

import time
import random
import string
import os

from seleniumbase import SB

# ===================== НАСТРОЙКИ =====================
OUTPUT_FILE = "mail_ee_accounts.txt"
DELAY_STEP = 5
DELAY_AFTER_CLICK = 7
# =====================================================

FIRST_NAMES = ["mari", "juri", "anna", "kristi", "tarmo", "liisa", "janek", "kadri", "rain", "silja", "marten", "merle", "andres", "triin", "priit"]
LAST_NAMES = ["jari", "tamm", "saar", "kask", "sepp", "mets", "pärn", "rebase", "ojamaa", "kallas", "mägi", "rand", "veski", "laur", "villems"]

def generate_username():
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    year = random.randint(1950, 2005)
    style = random.choice(['', '.', '_'])
    if style:
        return f"{first}{style}{last}{year}".lower()
    return f"{first}{last}{year}".lower()

def generate_password(length=14):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choices(chars, k=length))

def register_mail_ee():
    username = generate_username()
    password = generate_password()
    email = f"{username}@mail.ee"
    
    print(f"\n{'='*50}")
    print(f"[*] Регистрация: {email}")
    print(f"[*] Пароль: {password}")
    print(f"{'='*50}")
    
    with SB(uc=True, headless=False, headless2=False) as sb:
        
        # 1. Открыть страницу
        print("\n--- ЭТАП 1: Открытие страницы ---")
        sb.uc_open_with_reconnect("https://login.mail.ee/signup?go=portal", 30)
        print("[✓] Страница открыта")
        time.sleep(5)
        
        # 2. Принять куки (точный селектор id="accept-btn")
        print("\n--- ЭТАП 2: Принятие куки ---")
        try:
            sb.click("#accept-btn", timeout=10)
            print("[✓] Куки приняты (кнопка #accept-btn)")
        except:
            # Запасной вариант: поиск по тексту
            try:
                sb.click("NÕUSTUN", timeout=5)
                print("[✓] Куки приняты (по тексту)")
            except:
                try:
                    sb.click("Nõustun", timeout=5)
                    print("[✓] Куки приняты (по тексту)")
                except:
                    print("[!] Кнопка куки не найдена")
        time.sleep(3)
        
        # 3. Ввод имени пользователя
        print("\n--- ЭТАП 3: Ввод имени пользователя ---")
        try:
            sb.wait_for_element_visible("input[name='username']", timeout=15)
            sb.type("input[name='username']", username)
            print(f"[✓] Имя введено: {username}")
        except Exception as e:
            print(f"[-] Не найдено поле ввода имени: {e}")
            return False
        
        time.sleep(DELAY_STEP)
        
        # 4. Проверка доступности имени
        print("\n--- ЭТАП 4: Проверка доступности имени ---")
        try:
            sb.click("Kontrolli saadavust", timeout=5)
            print("[✓] Нажата кнопка проверки")
        except:
            print("[-] Не найдена кнопка проверки")
            return False
        
        time.sleep(DELAY_AFTER_CLICK)
        
        # Проверяем, свободно ли имя
        if sb.is_text_visible("pole saadaval", timeout=3):
            print("[-] Имя занято, пробуем другое...")
            return False
        
        # 5. Ввод пароля
        print("\n--- ЭТАП 5: Ввод пароля ---")
        try:
            sb.wait_for_element_visible("input[name='password']", timeout=10)
            sb.type("input[name='password']", password)
            print("[✓] Пароль введён")
        except:
            print("[-] Не найдено поле пароля")
            return False
        
        time.sleep(DELAY_STEP)
        
        # 6. Отметка галочек
        print("\n--- ЭТАП 6: Отметка галочек ---")
        try:
            checkboxes = sb.find_elements("//input[@type='checkbox']")
            print(f"[*] Найдено галочек: {len(checkboxes)}")
            for i, cb in enumerate(checkboxes):
                if not cb.is_selected():
                    sb.execute_script("arguments[0].click();", cb)
                    print(f"[✓] Галочка {i+1} отмечена")
                    time.sleep(1)
        except Exception as e:
            print(f"[!] Ошибка при отметке галочек: {e}")
        
        # 7. Создание аккаунта
        print("\n--- ЭТАП 7: Создание аккаунта ---")
        try:
            sb.click("Loo uus konto", timeout=5)
            print("[✓] Нажата кнопка создания аккаунта")
        except:
            print("[-] Не найдена кнопка создания аккаунта")
            return False
        
        time.sleep(5)
        
        # 8. Обработка hCaptcha
        print("\n--- ЭТАП 8: Обработка hCaptcha ---")
        try:
            if sb.uc_gui_click_captcha(timeout=10):
                print("[✓] hCaptcha чекбокс нажат автоматически")
            else:
                print("[!] Автоматический клик не сработал")
        except Exception as e:
            print(f"[!] Ошибка при обработке капчи: {e}")
        
        # Проверяем, появилась ли капча
        if sb.is_element_present("iframe[src*='captcha']", timeout=5):
            print("\n" + "!" * 50)
            print("🔐 РЕШИТЕ hCaptcha ВРУЧНУЮ В ОТКРЫТОМ БРАУЗЕРЕ")
            print("!" * 50)
            input("Нажмите Enter ПОСЛЕ решения капчи...")
        else:
            print("[✓] Капча не обнаружена")
        
        # Сохраняем аккаунт
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{email}:{password}\n")
        
        print(f"\n[+] Сохранён: {email}")
        return True

def main():
    print("=" * 60)
    print("Mail.ee Account Generator с SeleniumBase")
    print("Точный селектор куки: #accept-btn")
    print("=" * 60)
    
    # Проверяем DISPLAY
    if "DISPLAY" not in os.environ:
        os.environ["DISPLAY"] = ":0"
        print("[*] Установлен DISPLAY=:0")
    
    print(f"[*] Текущий DISPLAY: {os.environ.get('DISPLAY')}")
    
    print("\n⚠️ ВНИМАНИЕ:")
    print("   - Браузер будет ВИДИМ")
    print("   - Cloudflare обходится автоматически")
    print("   - Кнопка куки: #accept-btn")
    print("   - hCaptcha решается вручную")
    print("=" * 60)
    
    try:
        count = int(input("\nСколько аккаунтов создать: ") or 1)
    except:
        count = 1
    
    success = 0
    for i in range(count):
        print(f"\n{'#'*50}")
        print(f"Аккаунт {i+1}/{count}")
        print(f"{'#'*50}")
        
        if register_mail_ee():
            success += 1
        else:
            print(f"[-] Аккаунт {i+1} не создан")
        
        if i < count - 1:
            print(f"\n[*] Ожидание 20 секунд...")
            time.sleep(20)
    
    print("\n" + "=" * 60)
    print(f"✅ Готово! Создано: {success}/{count}")
    print(f"📁 Файл: {OUTPUT_FILE}")
    print("=" * 60)

if __name__ == "__main__":
    main()
