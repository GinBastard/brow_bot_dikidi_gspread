from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
# chrome_options = Options()
# chrome_options.add_argument("--headless")

import time
import pandas as pd
pd.set_option('display.expand_frame_repr', False)   # показывать все строки и столбцы без переносов
from tabulate import tabulate
import traceback


def get_dikidi_dates(url):
    try:
        driver = webdriver.Chrome()  # Используем Chrome, но вы можете выбрать другой браузер .Chrome(options=chrome_options)
        driver.get(url)

        # Находим div, внутри которого содержится текст "ещё"
        div_element = driver.find_element(By.XPATH, "//div[contains(text(), 'ещё')]")
        div_element.click()
        time.sleep(1)

        dates = []
        elements = driver.find_elements(By.CSS_SELECTOR, '[data-date]')
        i = 0
        for element in elements:
            i += 1
            if i > 10:   # Ограничение количества элементов для добавления (после нажатия видно только 9(10) элементов)
                break
            attribute_value = element.get_attribute('data-date')
            if attribute_value:
                dates.append(attribute_value)

        # Преобразование списка в множество, которое автоматически удаляет дубликаты
        unique_dates = list(set(dates))
        unique_dates.sort()
        #print(unique_dates)

        df_dikidi = pd.DataFrame(columns=['8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18'])

        date_time_dikidi = {}

        for date_ in dates:
                element_ = driver.find_element(By.CSS_SELECTOR, f"[data-date='{date_}']:not(.hide)")
                element_.click()
                time.sleep(1)
                times = driver.find_elements(By.CSS_SELECTOR, "span.nr-title")
                values = []
                for time_ in times:
                    values.append(time_.text)
                date_time_dikidi[date_] = values    # создали словарь с датами dikidi и временем работы

        # Загрузка данных из словаря в DataFrame
        for date, times in date_time_dikidi.items():
            #df_dikidi.at[date, 'Date'] = date

            for time_e in times:
                if time_e:
                    hour = int(time_e.split(':')[0])
                    min_ = int(time_e.split(':')[1])
                    if min_ >= 40:
                       hour += 1
                    df_dikidi.at[date, str(hour)] = time_e

        print('Дата фрейм dikidi:\n', tabulate(df_dikidi.fillna(''), headers='keys', tablefmt='pretty'))
        return df_dikidi.fillna('')

    except Exception as e:
        print(traceback.print_exc())
        print("Ошибка в получении данных с Dikidi (selenium)")
        return None




# url_4h = 'https://dikidi.ru/ru/record/658559?p=4.pi-po-sm-ss-sd&o=1&m=1505101&s=5918559&rl=0_0&source=widget'  # Замените URL на адрес нужного веб-сайта
# get_dikidi_dates(url_4h)