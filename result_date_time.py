# import gspread
# from google.oauth2.service_account import Credentials
# В ДОСТУП к файлу - обязательно добавить e-mail клиента - из проекта Google!!!
# scopes = [
#     'https://www.googleapis.com/auth/spreadsheets',
#     'https://www.googleapis.com/auth/drive'
# ]
# credentials = Credentials.from_service_account_file(
#     'E:\Trading\keys\mypython-412919-56da1c8c153b.json',    # путь к файлу json с ключом API Google
#     scopes=scopes
# )
# gc = gspread.authorize(credentials)
#====================================================================


import pandas as pd
pd.set_option('display.expand_frame_repr', False)   # показывать все строки и столбцы без переносов
from tabulate import tabulate
from datetime import datetime

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

# ВРЕМЕННО ...
# selected_procedure = 'Волоски'
# selected_place = 'Звездная'
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

    df_dikidi = dikidi.get_dikidi_dates(url)

    start_date = df_dikidi.index[0]
    end_date = df_dikidi.index[-1]

    df_plan = plan.get_plan_dates(start_date, end_date)

    # Нахождение общих индексов
    common_index = df_dikidi.index.intersection(df_plan.index)
    # Нахождение общих столбцов
    common_columns = df_dikidi.columns.intersection(df_plan.columns)
    # Создание пустого итогового датафрейма
    result_df = pd.DataFrame(index=common_index, columns=common_columns)

    # Заполнение итогового датафрейма значениями из df_dikidi, если значения совпадают, иначе пустыми значениями
    for col in common_columns:
        #result_df[col] = df_dikidi.loc[common_index, col].where(df_dikidi.loc[common_index, col] == df_plan.loc[common_index, col], '')
        result_df[col] = df_dikidi.loc[common_index, col]
        result_df[col] = result_df[col].where(result_df[col].str.split(':', expand=True)[0] == df_plan.loc[common_index, col].str.split(':', expand=True)[0], '')

    print('Дата фрейм result_df:\n', tabulate(result_df.fillna(''), headers='keys', tablefmt='pretty'))
    #print('Дата фрейм result_df:\n', tabulate(result_df.fillna(''), headers='keys', tablefmt='pretty'))


    df_schedule = schedule.get_schedule_dates(start_date, end_date)
    # print(df_schedule.info())
    #  Перед сравнением двух df, необходимо проверить, есть ли в df_schedule_m лишние ряды и удалить их, чтобы датафреймы были одинаковыми.
    # Найдем лишний ряд в df_schedule_m
    extra_index = df_schedule.index.difference(result_df.index)
    if not extra_index.empty:
        # Удалим лишний ряд из df_schedule
        df_schedule = df_schedule.drop(index=extra_index)

    # # Перед применением reindex() убедимся, что индексы обоих DataFrame упорядочены
    # result_df = result_df.sort_index()
    # df_schedule = df_schedule.sort_index()
    #
    # # Применим reindex() для приведения обоих DataFrame к общим индексам
    # result_df = result_df.reindex(index=result_df.index.union(df_schedule.index))
    # df_schedule = df_schedule.reindex(index=df_schedule.index)

    # print('====после удаления лишних рядов====')
    # print(tabulate(result_df, headers='keys', tablefmt='pretty'))
    # print(tabulate(df_schedule, headers='keys', tablefmt='pretty'))


    # Сравнение результирующего датафрейма с расписанием с помощью булевой алгебры и map - заполненные ячейки = True, пустые - False
    df_result_m = result_df.map(lambda x: True if x != '' else False)
    df_schedule_m = df_schedule.map(lambda x: True if x != '' else False)
    #
    # common_index = df_result_m.index.intersection(df_schedule_m.index)
    # common_columns = df_result_m.columns.intersection(df_schedule_m.columns)
    # df_result_m = df_result_m.reindex(index=common_index, columns=common_columns)
    # df_schedule_m = df_schedule_m.reindex(index=common_index, columns=common_columns)

    # Нахождение индексов, присутствующих в df1, но отсутствующих в df2
    #different_index = df_schedule_m.index.difference(df_result_m.index)
    # Нахождение столбцов, присутствующих в df1, но отсутствующих в df2
    #different_columns = df_schedule_m.columns.difference(df_result_m.columns)

    # Получение общих индексов двух датафреймов
    #common_index = df_schedule_m.index.intersection(df_result_m.index)

    # Получение общих столбцов двух датафреймов
    # common_columns = df_schedule_m.columns.intersection(df_result_m.columns)
    # print(f'различия индексов -{different_index}')
    # print(f'различия столбцов -{different_columns}')
    # print(f'сходство индексов -{common_index}')
    # print(f'сходство столбцов -{common_columns}')


    final_df = df_result_m != df_schedule_m  # Сравнение датафреймов
    final_df = final_df.where(final_df == False, result_df)  # Замена True значениями из result_df
    final_df = final_df.replace(False, '')  # Замена False на пустые строки

    print('Дата фрейм final_df:\n', tabulate(final_df.fillna(''), headers='keys', tablefmt='pretty'))
    return final_df

    # Возвращаем в brow_bot.py -  df_result с подготвленными допустимыми датами и временем

#print('Финал:\n', tabulate(result_date_time(selected_procedure, selected_place), headers='keys', tablefmt='pretty'))
#result_date_time(selected_procedure, selected_place)