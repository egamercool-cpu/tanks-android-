[app]

# (str) Название приложения
title = Super Pixel Tanks

# (str) Название пакета (только английские буквы, без пробелов)
package.name = supertanks

# (str) Домен пакета (уникальный идентификатор)
package.domain = org.test

# (str) Версия приложения
version = 0.1

# (str) Папка с исходным кодом (где лежит main.py)
source.dir = .

# (list) Расширения файлов, которые попадут в APK
# ВАЖНО: я добавил ttf (шрифты) и wav/mp3 (звуки)
source.include_exts = py,png,jpg,kv,atlas,ttf,wav,mp3

# (list) Библиотеки, которые нужно установить
# САМОЕ ГЛАВНОЕ: здесь только python3 и pygame
requirements = python3,pygame

# (str) Ориентация экрана (landscape - горизонтально, portrait - вертикально)
orientation = landscape

# (bool) Полный экран
fullscreen = 1

# (list) Разрешения Android (стандартные)
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE

# (int) Минимальная версия API Android (Android 5.0+)
android.minapi = 21

# (int) Целевая версия API Android (требуется Google Play)
android.api = 31

# (bool) Использовать --private хранилище (рекомендуется True)
android.private_storage = True

# (str) Presplash background color (цвет экрана загрузки)
android.presplash_color = #000000

# (list) Архитектуры процессоров (для современных телефонов)
# arm64-v8a - для новых, armeabi-v7a - для старых. 
# Если будет ошибка памяти при сборке, оставь только arm64-v8a
android.archs = arm64-v8a, armeabi-v7a

# (bool) Разрешить резервное копирование
android.allow_backup = True

# (str) Bootstrap (для Pygame используется sdl2)
p4a.bootstrap = sdl2

[buildozer]

# (int) Уровень логирования (2 = debug)
log_level = 2

# (int) Показывать предупреждение при запуске от root (0 = нет)
warn_on_root = 0
