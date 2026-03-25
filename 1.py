#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mail.ee Auto-Registrator с обходом Cloudflare
Использует undetected_chromedriver для имитации реального браузера
"""

import time
import random
import string
import os
import sys

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

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

def human_like_delay(min_sec=0.5, max_sec=1.5):
    """Случайная задержка для имитации человека"""
    time.sleep(random.uniform(min_sec, max_sec))

def register_mail_ee():
    username = generate_username()
    password = generate_password()
    email = f"{username}@mail.ee"
    
    print(f"\n{'='*50}")
    print(f"[*] Регистрация: {email}")
    print(f"[*] Пароль: {password}")
    print(f"{'='*50}")
    
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1280,720")
    
    # Используем undetected_chromedriver для обхода Cloudflare
    driver = uc.Chrome(options=options, version_main=None, use_subprocess=False)
    
    try:
        print("[1] Открываю страницу (ожидание Cloudflare)...")
        driver.get("https://login.mail.ee/signup?go=portal")
        time.sleep(8)  # Даём время Cloudflare
        
        wait = WebDriverWait(driver, 30)
        
        # 2. Принять куки
        try:
            cookie_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Nõustun')]")))
            human_like_mouse_move(driver, cookie_btn)
            cookie_btn.click()
            print("[2] Приняты куки")
            time.sleep(DELAY_AFTER_CLICK)
        except:
            print("[2] Кнопка куки не найдена")
        
        # 3. Имя пользователя
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        human_like_mouse_move(driver, username_field)
        username_field.clear()
        human_like_typing(username_field, username)
        print(f"[3] Введено имя: {username}")
        human_like_delay(1, 2)
        
        # 4. Проверить доступность
        check_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Kontrolli saadavust')]")))
        human_like_mouse_move(driver, check_btn)
        check_btn.click()
        print("[4] Нажата Kontrolli saadavust")
        time.sleep(DELAY_AFTER_CLICK)
        
        # 5. Пароль
        password_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        human_like_mouse_move(driver, password_field)
        password_field.clear()
        human_like_typing(password_field, password)
        print("[5] Пароль введён")
        human_like_delay(1, 2)
        
        # 6. Галочки
        checkboxes = driver.find_elements(By.XPATH, "//input[@type='checkbox']")
        for i, cb in enumerate(checkboxes):
            if not cb.is_selected():
                human_like_mouse_move(driver, cb)
                cb.click()
                print(f"[6] Отмечена галочка {i+1}")
                time.sleep(2)
        
        # 7. Создать аккаунт
        create_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Loo uus konto')]")))
        human_like_mouse_move(driver, create_btn)
        create_btn.click()
        print("[7] Нажата Loo uus konto")
        time.sleep(5)
        
        # 8. hCaptcha
        print("\n" + "!" * 50)
        print("🔐 РЕШИТЕ hCaptcha ВРУЧНУЮ В ОТКРЫТОМ БРАУЗЕРЕ")
        print("Если капча не появляется — Cloudflare заблокировал, попробуйте другой IP")
        print("!" * 50)
        input("Нажмите Enter ПОСЛЕ решения капчи...")
        
        # Сохраняем аккаунт
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{email}:{password}\n")
        
        print(f"[+] Успешно сохранён: {email}")
        return True
        
    except Exception as e:
        print(f"[-] Ошибка: {e}")
        return False
    finally:
        driver.quit()

def human_like_typing(element, text):
    """Имитирует набор текста с случайными задержками"""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.15))

def human_like_mouse_move(driver, element):
    """Имитирует движение мыши к элементу"""
    from selenium.webdriver.common.action_chains import ActionChains
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()
    time.sleep(random.uniform(0.3, 0.8))

def main():
    print("=" * 60)
    print("Mail.ee Account Generator (с обходом Cloudflare)")
    print("=" * 60)
    print("\n⚠️ ВАЖНО:")
    print("   - Используется undetected-chromedriver для обхода Cloudflare")
    print("   - hCaptcha решается ВРУЧНУЮ")
    print("   - Добавлены имитации движений мыши и задержек")
    print("=" * 60)
    
    try:
        count = int(input("\nСколько аккаунтов создать: ") or 1)
    except:
        count = 1
    
    for i in range(count):
        print(f"\n{'#'*50}")
        print(f"Аккаунт {i+1}/{count}")
        print(f"{'#'*50}")
        
        if register_mail_ee():
            print(f"[+] Аккаунт {i+1} создан")
        else:
            print(f"[-] Аккаунт {i+1} не создан")
        
        if i < count - 1:
            print(f"\n[*] Ожидание 10 секунд...")
            time.sleep(10)
    
    print("\n" + "=" * 60)
    print(f"✅ Готово! Аккаунты сохранены в {OUTPUT_FILE}")
    print("=" * 60)

if __name__ == "__main__":
    # Установка undetected-chromedriver если не установлен
    try:
        import undetected_chromedriver
    except ImportError:
        print("Устанавливаю undetected-chromedriver...")
        os.system("pip install undetected-chromedriver")
    
    main()
