import re
from datetime import datetime

from selenium import webdriver

# ТИХИЙ запуск вебдрайвера selenium
from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument('--no-sandbox')     # может быть полезным в ситуациях, когда Selenium WebDriver запускается в ограниченной среде, где доступ к песочнице может быть запрещен или вызывать проблемы
options.add_argument('--headless')       # может быть полезным, так как он обычно ускоряет процесс выполнения тестов и уменьшает потребление ресурсов компьютера. Однако, в некоторых случаях, элементы на странице могут отображаться или вести себя по-другому в режиме безголового браузера, что может вызывать проблемы при выполнении сценариев.
options.add_argument('--disable-dev-shm-usage')   # Chrome может использовать /dev/shm для хранения временных данных, таких как изображения или другие ресурсы. Однако, в некоторых средах или конфигурациях это может вызывать проблемы, особенно при ограниченных ресурсах.

# options.add_argument("start-maximized");
# options.add_argument("disable-infobars");
# options.add_argument("--disable-extensions");
# options.add_argument("--disable-gpu");
# options.add_argument("--disable-dev-shm-usage");

from selenium.webdriver.common.by import By


import time
import pandas as pd
pd.set_option('display.expand_frame_repr', False)   # показывать все строки и столбцы без переносов
from tabulate import tabulate
import traceback

# Проверка формата времени AM/PM
def is_am_pm_format(time_str):
    # Регулярное выражение для проверки формата AM/PM
    am_pm_pattern = re.compile(r'\b\d{1,2}:\d{2}\s*(AM|PM)\b', re.IGNORECASE)

    if re.match(am_pm_pattern, time_str):
        return True
    else:
        return False

def get_dikidi_dates(url):
    try:

        # запускаем драйвер Chrome в ТИХОМ режиме ((options=options) - опции указаны выше
        driver = webdriver.Chrome(options=options)


        driver.get(url)
        time.sleep(2)      # делаем паузу для прогрузки контента на странице в браузере
        # Явные ожидания с таймаутом в 5 секунд
        #wait = WebDriverWait(driver, 5)

        div_element = driver.find_element(By.CSS_SELECTOR, "div.nrs-color")


        div_element.click()
        time.sleep(1)      # делаем паузу для прогрузки контента на странице в браузере

        dates = []         # пустой список для дат
        elements = driver.find_elements(By.CSS_SELECTOR, '[data-date]')   # находим все элементы с атрибутом data-date (кнопки с датами на странице)
        i = 0
        for element in elements:            # перебираем элементы (кнопки с датами)
            i += 1
            if i > 10:   # Ограничение количества элементов для добавления (после нажатия видно только 9(10) элементов)
                break
            attribute_value = element.get_attribute('data-date')   # получаем название в атрибуте (дату)
            if attribute_value:
                dates.append(attribute_value)                      # если есть значение, добавляем в список дат

        # Преобразование списка в множество, которое автоматически удаляет дубликаты
        unique_dates = list(set(dates))                            # удаляем дубликаты
        unique_dates.sort()                                        # сортируем по возрастанию

        # Создаем датафрейм с обозначением заголовков столбцов
        df_dikidi = pd.DataFrame(columns=['8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18'])

        date_time_dikidi = {}          # словарь для хранения дат и времени (на эти даты)

        for date_ in dates:            # перебираем список добавленных дат
                element_ = driver.find_element(By.CSS_SELECTOR, f"[data-date='{date_}']:not(.hide)")  # находим кнопку с датой
                element_.click()                                 # нажимаем на нее
                time.sleep(1)                                    # делаем паузу для прогрузки контента на странице в браузере
                times = driver.find_elements(By.CSS_SELECTOR, "span.nr-title")   # находим все элементы span с временем
                values = []                                     # пустой список для времени
                for time_ in times:                             # перебираем элементы span с временем
                    values.append(time_.text)                   # добавляем в список время
                date_time_dikidi[date_] = values    # создаём словарь с датами dikidi и временем работы, помещаем в каждую дату (ключ) - список с временем


        driver.quit()  # Закрываем браузер

        # Загрузка данных из словаря в DataFrame
        for date, times in date_time_dikidi.items():  # перебираем словар: получаем ключи и значения из словаря дата-время
            for time_e in times:  # перебираем значения (списки времени)
                if time_e:
                    if is_am_pm_format(time_e):  # проверяем формат времени (AM/PM)
                        time_obj = datetime.strptime(time_e, '%I:%M %p')
                    else:
                        time_obj = datetime.strptime(time_e, '%H:%M')

                    hour = time_obj.hour  # разделяем время на часы и минуты
                    minute = time_obj.minute
                    if minute >= 40:  # если минуты больше или равны 40, то переносим на следующий час (16:40 -> 17:00)
                        hour += 1
                    time_str = time_obj.strftime('%H:%M')
                    df_dikidi.at[date, str(hour)] = time_str  # добавляем в датафрейм дату и время

                # выводим датафрейм разграфленный (tabulate)
        print('Дата фрейм dikidi:\n', tabulate(df_dikidi.fillna(''), headers='keys', tablefmt='pretty'))
        return df_dikidi.fillna('')  # возвращаем датафрейм (None заменяем на пустую строку)

    except Exception as e:
        print(traceback.print_exc())
        print("Ошибка в получении данных с Dikidi (selenium)")
        return None
