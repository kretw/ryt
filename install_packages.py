import subprocess
import sys

# Функция для установки пакета
def install_package(package_name):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"Успешно установлено: {package_name}")
    except Exception as e:
        print(f"Не удалось установить {package_name}. Ошибка: {e}")

# Список необходимых библиотек
required_packages = [
    "flask",             # Для работы Flask
    "flask_sqlalchemy",  # Для работы с базой данных SQLAlchemy
    "pandas",            # Для работы с табличными данными
    "openpyxl"           # Для экспорта Excel-файлов
]

# Установка каждой библиотеки
for package in required_packages:
    install_package(package)
