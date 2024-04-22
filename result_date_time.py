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
    #df_schedule = schedule.get_schedule_dates()

    # Соединяем датафреймы по дате
    df_result = df_dikidi.merge(df_plan, left_index=True, right_index=True, how='inner')
    # Убираем лишние столбцы из merged_df
    df_result = df_result[['8_x', '9_x', '10_x', '11_x', '12_x', '13_x', '14_x', '15_x', '16_x', '17_x', '18_x']]

    # Переименовываем столбцы
    df_result.columns = ['8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18']

    # Соединение df_dikidi, df_plan, df_schedule
    #df_result = pd.concat([df_dikidi, df_plan, df_schedule], axis=1)
    #df_result = df_result.dropna()

    return df_result
    # Возвращаем в tg_bot.py -  df_result с подготвленными допустимыми датами и временем

print('Результат:\n', result_date_time(selected_procedure, selected_place))