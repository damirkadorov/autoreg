#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mail.ee Auto-Registrator с SeleniumBase
Автоматический обход Cloudflare + надёжное принятие куки
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

# Реалистичные имена
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
    """Регистрирует один аккаунт с SeleniumBase"""
    
    username = generate_username()
    password = generate_password()
    email = f"{username}@mail.ee"
    
    print(f"\n{'='*50}")
    print(f"[*] Регистрация: {email}")
    print(f"[*] Пароль: {password}")
    print(f"{'='*50}")
    
    # Используем SeleniumBase с UC Mode
    with SB(uc=True, ad_block_on=True, incognito=True) as sb:
        
        # 1. Открыть страницу с обходом Cloudflare
        print("\n--- ЭТАП 1: Открытие страницы (обход Cloudflare) ---")
        sb.uc_open_with_reconnect("https://login.mail.ee/signup?go=portal", 15)
        print("[✓] Cloudflare обойдена")
        time.sleep(3)
        
        # Ждём полной загрузки страницы после Cloudflare
        sb.wait_for_ready_state_complete()
        print("[✓] Страница загружена")
        time.sleep(2)
        
        # 2. Принять куки (множественные селекторы)
        print("\n--- ЭТАП 2: Принятие куки ---")
        cookie_accepted = False
        
        cookie_selectors = [
            "//button[contains(text(), 'Nõustun')]",
            "//button[contains(text(), 'Accept')]",
            "//button[contains(text(), 'OK')]",
            "//button[contains(text(), 'Sulge')]",
            "//button[contains(@class, 'accept')]",
            "//a[contains(text(), 'Nõustun')]",
            "//button[@id='cookie-accept']",
            "//div[contains(@class, 'cookie')]//button"
        ]
        
        for selector in cookie_selectors:
            try:
                if sb.is_element_visible(selector, timeout=3):
                    sb.click(selector)
                    print(f"[✓] Куки приняты (селектор: {selector[:50]})")
                    cookie_accepted = True
                    time.sleep(2)
                    break
            except:
                continue
        
        if not cookie_accepted:
            print("[!] Кнопка куки не найдена, продолжаем...")
        
        # Ждём стабилизации после принятия куки
        time.sleep(2)
        
        # 3. Ввод имени пользователя
        print("\n--- ЭТАП 3: Ввод имени пользователя ---")
        try:
            # Ждём поле ввода
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
            sb.click("//button[contains(text(), 'Kontrolli saadavust')]")
            print("[✓] Нажата Kontrolli saadavust")
        except:
            # Пробуем другой селектор
            try:
                sb.click("//button[contains(@class, 'check')]")
                print("[✓] Нажата кнопка проверки (альт. селектор)")
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
        checkboxes = sb.find_elements("//input[@type='checkbox']")
        for i, cb in enumerate(checkboxes):
            if not cb.is_selected():
                try:
                    sb.click(cb)
                    print(f"[✓] Галочка {i+1} отмечена")
                    time.sleep(1.5)
                except:
                    print(f"[!] Не удалось отметить галочку {i+1}")
        
        # 7. Создание аккаунта
        print("\n--- ЭТАП 7: Создание аккаунта ---")
        try:
            sb.click("//button[contains(text(), 'Loo uus konto')]")
            print("[✓] Нажата Loo uus konto")
        except:
            try:
                sb.click("//button[@type='submit']")
                print("[✓] Нажата кнопка отправки")
            except:
                print("[-] Не найдена кнопка создания аккаунта")
                return False
        
        time.sleep(5)
        
        # 8. Обработка hCaptcha
        print("\n--- ЭТАП 8: Обработка hCaptcha ---")
        try:
            # Пробуем автоматически кликнуть на чекбокс капчи
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
            print("[✓] Капча не обнаружена или уже решена")
        
        # Проверка успешности регистрации
        time.sleep(3)
        current_url = sb.get_current_url()
        
        if "login" in current_url or "portal" in current_url:
            print("[+] Регистрация успешна!")
            
            # Сохраняем аккаунт
            with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
                f.write(f"{email}:{password}\n")
            
            print(f"\n[+] Сохранён: {email}")
            return True
        else:
            print("[-] Возможно, регистрация не завершена")
            return False

def main():
    print("=" * 60)
    print("Mail.ee Account Generator с SeleniumBase")
    print("Автоматический обход Cloudflare + надёжное принятие куки")
    print("=" * 60)
    print("\n⚠️ ВНИМАНИЕ:")
    print("   - Cloudflare обходится АВТОМАТИЧЕСКИ")
    print("   - Куки принимаются автоматически")
    print("   - hCaptcha требует РУЧНОГО решения")
    print("   - Между шагами задержка 5-7 секунд")
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
