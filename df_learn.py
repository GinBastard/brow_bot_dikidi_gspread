import pandas as pd
pd.set_option('display.expand_frame_repr', False)   # показывать все строки и столбцы без переносов
from tabulate import tabulate

data = {
    8: [None, None, None, None],
    9: ['10:00', '10:00', '10:00', None],
    10: ['11:00', '11:00', '11:00', None],
    11: ['12:00', '12:00', '12:00', None],
    12: [None, None, None, '13:00'],
    13: [None, None, None, '14:00'],
    14: [None, None, None, None],
    15: ['15:00', None, None, None],
    16: [None, None, None, None],
    17: [None, None, None, '18:00'],
    18: [None, None, None, None]
}

index = ['24-04-2024', '25-04-2024', '27-04-2024', '28-04-2024']

result_df = pd.DataFrame(data, index=index)
result_df = result_df.fillna('')

data2 = {
    8: [None, None, None, None, None],
    9: ['занято', 'занято', 'занято', None, None],
    10: [None, 'занято', 'занято', None, None],
    11: [None, None, None, 'занято', None],
    12: [None, None, None, 'занято', 'занято'],
    13: [None, None, None, None, None],
    14: [None, None, None, None, None],
    15: [None, None, None, 'занято', None],
    16: [None, None, None, 'занято', None],
    17: [None, None, None, None, None],
    18: [None, None, 'занято', 'занято', None]
}

index2 = ['24-04-2024', '25-04-2024', '26-04-2024', '27-04-2024', '28-04-2024']

df_schedule = pd.DataFrame(data2, index=index2)
df_schedule = df_schedule.fillna('')


print(f"===== result_df ДО УДАЛЕНИЯ ИНДЕКСА\n {tabulate(result_df, headers='keys', tablefmt='pretty')}")
print(result_df.info())
print(f"===== df_schedule ДО УДАЛЕНИЯ ИНДЕКСА\n {tabulate(df_schedule, headers='keys', tablefmt='pretty')}")
print(df_schedule.info())
# Найдем лишний ряд в df_schedule_m
extra_index = df_schedule.index.difference(result_df.index)
if not extra_index.empty:
        # Удалим лишний ряд из df_schedule
        df_schedule = df_schedule.drop(index=extra_index)

        # Перед применением reindex() убедимся, что индексы обоих DataFrame упорядочены
        result_df = result_df.sort_index()
        df_schedule = df_schedule.sort_index()

        # Применим reindex() для приведения обоих DataFrame к общим индексам
        result_df = result_df.reindex(index=result_df.index.union(df_schedule.index))
        df_schedule = df_schedule.reindex(index=df_schedule.index)



print(f"===== result_df ПОСЛЕ УДАЛЕНИЯ ИНДЕКСА\n {tabulate(result_df, headers='keys', tablefmt='pretty')}")
print(f"===== df_schedule ПОСЛЕ УДАЛЕНИЯ ИНДЕКСА\n {tabulate(df_schedule, headers='keys', tablefmt='pretty')}")


# for index, row in df_schedule.iterrows():
#     print(f"Index: {index}")
#     for index2, row2 in df_result.iterrows():
#         if index == index2:
#             for column, value in row.items():
#                 if value != '':
#                     df_result.loc[index, column] = ''
#                     # print(f"Column: {column}, Value: {value}")
#     #print(row)
#     # Здесь вы можете выполнять операции с каждым рядом

df_result_m = result_df.map(lambda x: True if x != '' else False)
df_schedule_m = df_schedule.map(lambda x: True if x != '' else False)

print(f"------ df_result_m True False\n {tabulate(df_result_m, headers='keys', tablefmt='pretty')}")
print(f"------ df_schedule_m True False\n {tabulate(df_schedule_m, headers='keys', tablefmt='pretty')}")



final_df = df_result_m != df_schedule_m
final_df = final_df.where(final_df == False, result_df)
final_df = final_df.replace(False, '')

print(f"------ final_df ПОСЛЕ ОБРАБОТКИ\n {tabulate(final_df, headers='keys', tablefmt='pretty')}")
# first_index = df_result.index[0]
# print("Первый индекс:", first_index)
# last_index = df_result.index[-1]
# print("Последний индекс:", last_index)