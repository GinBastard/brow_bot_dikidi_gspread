import pandas as pd
pd.set_option('display.expand_frame_repr', False)   # показывать все строки и столбцы без переносов

import get_dikidi as dikidi          # get_dikidi_dates(url)
import get_gs_plan as plan           # get_plan_dates()
import get_gs_schedule as schedule   # get_schedule_dates()

# ссылки на фреймы dikidi:
url_zvezdn_4h = 'https://dikidi.ru/ru/record/658559?p=4.pi-po-sm-ss-sd&o=1&m=1505101&s=5918559&rl=0_0&source=widget'


# ВРЕМЕННО ...
selected_procedure = 'Межресничка'
selected_place = 'Звездная'
def result_date_time(selected_procedure, selected_place):

    if selected_place == 'Звездная' and selected_procedure == 'Межресничка':
        url = url_zvezdn_4h



    df_dikidi = dikidi.get_dikidi_dates(url)

    # !!! здесь получить даты - первую и последнюю из df_dikidi , переформатирвать их, и вставить в plan.get_plan_dates() и schedule.get_schedule_dates()

    df_plan = plan.get_plan_dates()
    df_schedule = schedule.get_schedule_dates()

    # Нахождение общих индексов
    common_index = df_dikidi.index.intersection(df_plan.index)

    # Нахождение общих столбцов
    common_columns = df_dikidi.columns.intersection(df_plan.columns)

    # Создание пустого итогового датафрейма
    result_df = pd.DataFrame(index=common_index, columns=common_columns)

    # Заполнение итогового датафрейма значениями из df_dikidi, если значения совпадают, иначе пустыми значениями
    for col in common_columns:
        result_df[col] = df_dikidi.loc[common_index, col].where(df_dikidi.loc[common_index, col] == df_plan.loc[common_index, col], '')


    #return result_df

    print('Результат:\n', result_df)

    # Нахождение общих индексов
    common_index = result_df.index.intersection(df_schedule.index)

    # Нахождение общих столбцов
    common_columns = result_df.columns.intersection(df_schedule.columns)

    # Создание пустого итогового датафрейма
    final_df = pd.DataFrame(index=common_index, columns=common_columns)

    # Заполнение итогового датафрейма final_df значениями из result_df, если значения в df_schedule пусты
    for col in common_columns:
        final_df[col] = result_df.loc[common_index, col]

    print(f'result_df (2, 4): {df_schedule.iloc[2, 3]} - {type(df_schedule.iloc[2, 3])}, [ {df_schedule.iloc[2, 2]} ] - {type(df_schedule.iloc[2, 2])}')

    return final_df
    # Возвращаем в tg_bot.py -  df_result с подготвленными допустимыми датами и временем

print('Финал:\n', result_date_time(selected_procedure, selected_place))