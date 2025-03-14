import os
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from dotenv import load_dotenv 

VIDEO_DIR = "downloads"  # Папка с видео
BOOSTY_USERNAME = os.getenv("BOOSTY_USERNAME")

def get_latest_video():
    """Получаем последний скачанный файл"""
    files = [f for f in os.listdir(VIDEO_DIR) if f.endswith(".mp4")]
    if not files:
        print("❌ Нет видео для загрузки!")
        return None
    latest_file = max(files, key=lambda f: os.path.getctime(os.path.join(VIDEO_DIR, f)))
    return os.path.join(VIDEO_DIR, latest_file)

def generate_teaser(filename):
    """Генерирует текст тизера из имени файла"""
    name_without_extension = filename.replace(".mp4", "")
    teaser_text = name_without_extension.replace("_", " ")
    teaser_text = re.sub(r'\b(мерч|тг)\b', '', teaser_text)
    teaser_text = ' '.join(teaser_text.split())  # Убираем двойные пробелы
    return teaser_text

# Подключаемся к открытому браузеру Edge
edge_options = Options()
edge_options.debugger_address = "localhost:9222"

driver = webdriver.Edge(options=edge_options)
wait = WebDriverWait(driver, 15)

try:
    # 1️⃣ Открываем страницу создания поста
    driver.get("https://boosty.to/{BOOSTY_USERNAME}/new-post")

    # 2️⃣ Ждем и заполняем поле теги
    print("⌛ Ожидание поля для тегов...")
    tags_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Вводите теги через Enter (не более 10)']")))

    # Вводим "стрим" и нажимаем Enter
    print("📝 Вводим тег 'стрим'...")
    tags_field.send_keys("стрим")
    tags_field.send_keys(Keys.RETURN)

    # Вводим дату в формате дд.мм.гггг
    current_date = datetime.now().strftime("%d.%m.%Y")
    print(f"📝 Вводим дату {current_date}...")
    tags_field.send_keys(current_date)
    tags_field.send_keys(Keys.RETURN)

    # 3️⃣ Получаем название видео
    video_path = get_latest_video()
    if not video_path:
        driver.quit()
        exit()

    video_name = os.path.basename(video_path)
    teaser_text = generate_teaser(video_name)
    print(f"📌 Заголовок/тизер: {teaser_text}")

    # 4️⃣ Ждем и заполняем заголовок поста
    print("⌛ Ожидание поля заголовка...")
    title_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Введите заголовок поста']")))

    print("📝 Заполняем заголовок...")
    title_field.send_keys(teaser_text)

    # 5️⃣ Ждем и заполняем тизер поста
    print("⌛ Ожидание поля тизера...")
    teaser_field = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@data-placeholder='Начните писать тизер']")))

    print("📝 Заполняем тизер...")
    driver.execute_script("arguments[0].innerText = arguments[1];", teaser_field, teaser_text)
    time.sleep(2)  # Даем время для обновления интерфейса

    # 6️⃣ Ждем кнопку "Видео" и нажимаем
    print("⌛ Ожидание кнопки 'Видео'...")
    video_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(), 'Видео')]]")))

    print("✅ Кнопка найдена! Нажимаем...")
    video_button.click()
    time.sleep(2)  # Ждем, чтобы меню открылось

    # 7️⃣ Ждем кнопку "Загрузить файлом" и нажимаем
    print("⌛ Ожидание кнопки 'Загрузить файлом'...")
    upload_file_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Загрузить файлом')]")))

    print("✅ Кнопка найдена! Нажимаем...")
    upload_file_button.click()

    # 8️⃣ Ждем input для загрузки файла
    file_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))

    # 9️⃣ Загружаем видео
    print(f"📤 Загружаем видео: {video_path}")
    file_input.send_keys(os.path.abspath(video_path))
    time.sleep(10)  # Ждем загрузку

    # 🔟 Ожидание кнопки "Опубликовать"
    print("⌛ Ожидание кнопки 'Опубликовать'...")
    publish_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Опубликовать')]")))

    print("✅ Нажимаем 'Опубликовать'...")
    publish_button.click()

    print("✅ Видео загружено на Boosty!")

finally:
    time.sleep(5)
    driver.quit()
