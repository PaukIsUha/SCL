import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import sqlite3

API_TOKEN = '6688793178:AAHJYpnizrycS29Jl0HxIYH8eBRRLfKei8o'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_choices = {}
nums_data = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34']
nums_dict = {'1': nums_data[:8],
             '2': nums_data[:34],
             '3': nums_data[:24],
             '4': nums_data[:33]}

names_dict = {'1': 'Categories',
              '2': 'Subcategories',
              '3': 'Providers',
              '4': 'Products'}

id_post_dict = {'1': 'id_category',
                '2': 'id_subcategory',
                '3': 'id_provider',
                '4': 'id_product'}


async def getter_db_rows(id_name, table_name):
    connect = sqlite3.connect("Labels_data.db")
    cursor = connect.cursor()
    cursor.execute('''SELECT ''' + id_name + ''', name FROM ''' + table_name)
    full_products = '''
    '''
    for i in cursor.fetchall():
        full_products += str(i[0])
        full_products += ') '
        full_products += i[1]
        full_products += '''
        '''
    connect.close()
    return full_products


async def get_selections():
    return '''
    1) Categories
    2) Subcategories
    3) Providers
    4) Products'''


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    user_choices[message.from_user.id] = {}
    full_selection = await get_selections()
    await message.answer('''Добрый день! Выберите карточку:''' + full_selection)


async def choose_selection(message: types.Message, table_id):
    full_categories = await getter_db_rows(id_post_dict[table_id], names_dict[table_id])
    await message.answer('''Выберите категорию:''' + full_categories)


async def get_description(table_id, object_id):
    connect = sqlite3.connect("Labels_data.db")
    cursor = connect.cursor()
    cursor.execute('''SELECT description FROM ''' + names_dict[table_id] + ''' WHERE '''
                   + id_post_dict[table_id] + '''=''' + object_id)
    desc = cursor.fetchone()[0] if not (cursor.fetchone()[0] is None) else 'None'
    connect.close()
    return "*" + desc + "*"


async def desc_answer(message, desc):
    await message.answer("Текущее описание объекта:\n" + desc + "\nДля изменения напишите /edit", parse_mode=types.ParseMode.MARKDOWN)


@dp.message_handler(lambda message: message.text in nums_data)
async def choose_product(message: types.Message):
    user_choice = message.text
    user_id = message.from_user.id
    previous_choice = user_choices.get(user_id, {})
    if 'selection' not in previous_choice:
        if user_choice not in nums_data[:4]:
            await message.answer('''Index not in range''')
            await cmd_start(message)
        else:
            user_choices[user_id] = {'selection': user_choice}
            await choose_selection(message, user_choice)
    elif 'id_selection' not in previous_choice:
        if user_choice not in nums_dict[previous_choice['selection']]:
            await message.answer('''Index not in range''')
            await choose_selection(message, previous_choice['selection'])
        else:
            user_choices[user_id]['id_selection'] = user_choice
            await desc_answer(message,
                              await get_description(user_choices[user_id]['selection'],
                                                    user_choices[user_id]['id_selection']))


@dp.message_handler(commands=['edit'])
async def cmd_edit(message: types.Message):
    if message.from_user.id not in user_choices:
        await cmd_start(message)
    elif 'selection' not in user_choices[message.from_user.id] or 'id_selection' not in user_choices[message.from_user.id]:
        await message.answer('''Вы не выбрали объект''')
        await cmd_start(message)
    else:
        user_choices[message.from_user.id]['edit'] = 'start'
        await message.answer('''Введите новое описание''')


@dp.message_handler(commands=['cancel'])
async def cmd_cancel(message: types.Message):
    await cmd_start(message)


@dp.message_handler(commands=['commit'])
async def cmd_commit(message: types.Message):
    if message.from_user.id in user_choices:
        user_id = message.from_user.id
        if 'selection' in user_choices[user_id] and 'id_selection' in user_choices[user_id] and 'value' in user_choices[user_id]:
            except_process = await update_description(user_choices[user_id]['selection'],
                                     user_choices[user_id]['id_selection'],
                                     user_choices[user_id]['value'])
            if not except_process:
                await message.answer('''Обновление выполнено''')
    return



async def update_description(table_id, object_id, new_value):
    connect = sqlite3.connect("Labels_data.db")
    cursor = connect.cursor()
    cursor.execute('''UPDATE ''' + names_dict[table_id] + ''' SET description=\'''' + new_value + '''\' WHERE '''
                   + id_post_dict[table_id] + '''=''' + object_id)
    connect.commit()
    connect.close()
    return 0


@dp.message_handler()
async def handle_message(message: types.Message):
    if message.from_user.id in user_choices:
        user_id = message.from_user.id
        if 'edit' in user_choices[user_id]:
            if user_choices[user_id]['edit'] == 'start':
                user_choices[user_id]['edit'] = 'stop'
                user_choices[user_id]['value'] = message.text
                await message.answer("Старое описание:\n" +
                                     await get_description(user_choices[user_id]['selection'],
                                                           user_choices[user_id]['id_selection']) +
                                     "\nНовое описание\n*" + user_choices[user_id]['value'] +
                                     "*\n Для коммита введите /commit, а для отмены введите /cancel", parse_mode=types.ParseMode.MARKDOWN)
    return

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
