from selenium import webdriver
from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# chrome_options = Options()
# chrome_options.add_argument("--headless")

import time
import pandas as pd
pd.set_option('display.expand_frame_repr', False)   # показывать все строки и столбцы без переносов
from tabulate import tabulate
import traceback


def get_dikidi_dates(url):
    try:
        driver = webdriver.Chrome()  # Используем Chrome
        driver.get(url)

        # Находим div, внутри которого содержится текст "ещё"
        div_element = driver.find_element(By.XPATH, "//div[contains(text(), 'ещё')]")
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

        # Загрузка данных из словаря в DataFrame
        for date, times in date_time_dikidi.items():       # перебираем словар: получаем ключи и значения из словаря дата-время
            for time_e in times:                           # перебираем значения (списки времени)
                if time_e:
                    hour = int(time_e.split(':')[0])       # разделяем время на часы и минуты
                    min_ = int(time_e.split(':')[1])
                    if min_ >= 40:                         # если минуты больше или равны 40, то переносим на следующий час (16:40 -> 17:00)
                       hour += 1
                    df_dikidi.at[date, str(hour)] = time_e    # добавляем в датафрейм дату и время

                # выводим датафрейм разграфленный (tabulate)
        print('Дата фрейм dikidi:\n', tabulate(df_dikidi.fillna(''), headers='keys', tablefmt='pretty'))
        return df_dikidi.fillna('')  # возвращаем датафрейм (None заменяем на пустую строку)

    except Exception as e:
        print(traceback.print_exc())
        print("Ошибка в получении данных с Dikidi (selenium)")
        return None
