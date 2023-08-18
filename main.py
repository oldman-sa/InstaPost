from instagrapi import Client
from instagrapi.exceptions import TwoFactorRequired, PleaseWaitFewMinutes
from time import sleep
from PIL import Image
import pytesseract
import os
import sys
import random

# Ввод учетных данных
username = input("Введите ваше имя пользователя: ")
password = input("Введите ваш пароль: ")

# Создание объекта api
api = Client()

try:
    # Попытка авторизации
    api.login(username, password)
    print("\033[33mLogin Successful!\n\033[39m")
except TwoFactorRequired:
    verification_code = input("Введите код верификации: ")
    api.login(username, password, verification_code=verification_code)
    print("\033[33mLogin Successful!\n\033[39m")
except PleaseWaitFewMinutes as wait_error:
    print(wait_error)
    print("Пожалуйста, подождите несколько минут и попробуйте снова.")
    sys.exit()
except Exception as e:
    print('Login Failed!?')
    print(f'Error: {e}\n')
    sys.exit()

# Папка с фотографиями для публикации
photo_folder = input("Введите путь к файлу (если папка находится в директории со скриптом, то путь будет таким 'photos/' ): ")

# Получение списка файлов в папке
photo_files = os.listdir(photo_folder)

# Проходим по каждому файлу и публикуем его
for photo_file in photo_files:
    if photo_file.endswith(('.jpg', '.png', '.jpeg')):  # Проверяем наличие расширения изображения
        photo_path = os.path.join(photo_folder, photo_file)
        try:
            original_image = Image.open(photo_path)
            text = pytesseract.image_to_string(original_image)

            # Измените размеры и обрежьте изображение с учетом допустимого соотношения сторон
            target_aspect_ratio = 4 / 5  # Пример: 4:5 соотношение
            width, height = original_image.size
            new_width = min(width, int(height * target_aspect_ratio))
            new_height = min(height, int(width / target_aspect_ratio))

            resized_image = original_image.resize((new_width, new_height), Image.LANCZOS)

            # Обрежьте верхнюю и нижнюю части изображения (на 10% каждая)
            top_crop = int(0.1 * new_height)
            bottom_crop = new_height - top_crop
            cropped_image = resized_image.crop((0, top_crop, new_width, bottom_crop))

            # Сохраните измененное изображение
            cropped_photo_path = os.path.join(photo_folder, f"cropped_{photo_file}")
            cropped_image.save(cropped_photo_path)

            media = api.photo_upload(cropped_photo_path, caption=text)
            print(f"\033[32mУспех\033[39m: Фото {photo_file} успешно опубликовано с подписью '{text}'!")
            # Очистите память, удалив измененное изображение
            os.remove(cropped_photo_path)
            sleep(1)
        except Exception as e:
            print(f"\033[31mОшибка\033[39m при публикации фото {photo_file}: {e}")
            sleep(1)

# Выход из аккаунта
api.logout()
