import pandas as pd
pd.set_option('display.expand_frame_repr', False)   # показывать все строки и столбцы без переносов
from tabulate import tabulate

import get_dikidi as dikidi          # get_dikidi_dates(url)
import get_gs_plan as plan           # get_plan_dates()
import get_gs_schedule as schedule   # get_schedule_dates()

# ссылки на фреймы dikidi:
url_zvezdn_2h = 'https://dikidi.ru/ru/record/658559?p=4.pi-po-sm-ss-sd&o=1&m=1505103&s=5918615&rl=0_0&source=widget'
url_zvezdn_4h = 'https://dikidi.ru/ru/record/658559?p=4.pi-po-sm-ss-sd&o=1&m=1505103&s=5918625&rl=0_0&source=widget'
url_push_2h = 'https://dikidi.net/686867?p=2.pi-ssm-sd&o=10&m=2352562&s=10102456&rl=0_undefined'
url_push_4h = 'https://dikidi.net/686867?p=2.pi-mi-sd&o=11&m=2352562&s=10102534&rl=0_undefined'

procedures = ['Межресничка', 'Волоски', 'Гиперреализм', 'Пудровое']
places = ['Звездная', 'Пушкин']

def result_date_time(selected_procedure, selected_place):

    # выбор нужного url расписания на dikidi в зависимости от услуги (продолжительности) и места
    if selected_place == 'Звездная' and selected_procedure == 'Межресничка':
        url = url_zvezdn_2h
    elif selected_place == 'Звездная' and selected_procedure == 'Волоски':
        url = url_zvezdn_2h
    elif selected_place == 'Звездная' and selected_procedure == 'Гиперреализм':
        url = url_zvezdn_2h
    elif selected_place == 'Звездная' and selected_procedure == 'Пудровое':
        url = url_zvezdn_2h
    elif selected_place == 'Пушкин' and selected_procedure == 'Межресничка':
        url = url_push_2h
    elif selected_place == 'Пушкин' and selected_procedure == 'Волоски':
        url = url_push_2h
    elif selected_place == 'Пушкин' and selected_procedure == 'Гиперреализм':
        url = url_push_2h
    elif selected_place == 'Пушкин' and selected_procedure == 'Пудровое':
        url = url_push_2h
    else:
        url = ''
        print('Неизвестная комбинация услуги и места')

    df_dikidi = dikidi.get_dikidi_dates(url)   # передаем выбранный url в функцию get_dikidi_dates, получаем данные о свободных даты-времени

          # вычисляем начальную и конечную дату (первый и последний индекс (дату) датафрейма
    start_date = df_dikidi.index[0]
    end_date = df_dikidi.index[-1]

    df_plan = plan.get_plan_dates(start_date, end_date)                  # передаем полученный даты в функцию get_plan_dates, получаем датафрейм с Графиком работы
    common_index = df_dikidi.index.intersection(df_plan.index)           # Нахождение общих индексов
    common_columns = df_dikidi.columns.intersection(df_plan.columns)     # Нахождение общих столбцов
    result_df = pd.DataFrame(index=common_index, columns=common_columns) # Создание пустого итогового датафрейма

          # Заполнение итогового датафрейма значениями из df_dikidi, если значения совпадают, иначе пустыми значениями
    for col in common_columns:
        result_df[col] = df_dikidi.loc[common_index, col]
        result_df[col] = result_df[col].where(result_df[col].str.split(':', expand=True)[0] == df_plan.loc[common_index, col].str.split(':', expand=True)[0], '')
         # выводим итоговый разграфленный датафрейм
    print('Дата фрейм result_df:\n', tabulate(result_df.fillna(''), headers='keys', tablefmt='pretty'))

         # Передаем даты в функцию get_schedule_dates, Получаем датафрейм с расписанием из файла get_gs_schedule.py
    df_schedule = schedule.get_schedule_dates(start_date, end_date)

         # Перед сравнением двух df, необходимо проверить, есть ли в df_schedule_m лишние ряды и удалить их, чтобы датафреймы были одинаковыми.
    extra_index = df_schedule.index.difference(result_df.index)    # Найдем лишний ряд в df_schedule_m
    if not extra_index.empty:
        df_schedule = df_schedule.drop(index=extra_index)          # Удалим лишний ряд из df_schedule

         # Сравнение результирующего датафрейма с расписанием с помощью булевой алгебры и map - заполненные ячейки = True, пустые - False
    df_result_m = result_df.map(lambda x: True if x != '' else False)
    df_schedule_m = df_schedule.map(lambda x: True if x != '' else False)

    final_df = df_result_m != df_schedule_m                  # Сравнение датафреймов ДОЛЖНЫ БЫТЬ ОДИНАКОВЫМИ ПО ИНДЕКСАМ И СТОЛБЦАМ!!!
    final_df = final_df.where(final_df == False, result_df)  # Замена True значениями из result_df
    final_df = final_df.replace(False, '')                   # Замена False на пустые строки

    df_final = final_df.fillna('')
    # Выводим финальный разграфленный датафрейм
    print('Дата фрейм df_final:\n', tabulate(df_final.fillna(''), headers='keys', tablefmt='pretty'))

    return df_final      # Возвращаем финальный  датафрейм, заполненный в пустотах - пустыми строками