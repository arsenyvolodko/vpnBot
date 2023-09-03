import schedule
import time
import datetime

from files import Files

# Ваш код для создания и настройки бота

# Функция, которую вы хотите вызывать раз в сутки
# def daily_task():
#     print('pososi')
#     print(datetime.datetime.now())
#     pass

# Запланируйте выполнение функции daily_task каждый день в определенное время (например, в 12:00)
schedule.every().day.at("17:35:50").do(daily_task)

# Основной цикл программы
# while True:
#     schedule.run_pending()  # Проверяем, есть ли запланированные задачи
#     time.sleep(10)  # Пауза, чтобы не нагружать процессор

# Запустите ваш бот и оставьте этот цикл работать в фоновом режиме
