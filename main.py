# main.py
import telebot
from telebot import types
import logic

API_TOKEN = 'ВАШ_ТОКЕН_ЗДЕСЬ'

bot = telebot.TeleBot(API_TOKEN)

user_states = {}  # Хранение состояний пользователей

# --- КЛАВИАТУРЫ ---
def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_create = types.KeyboardButton("📁 Создать папку")
    btn_multi = types.KeyboardButton("➕ Множественное создание")
    btn_list = types.KeyboardButton("🔍 Просмотр файловой системы")
    markup.add(btn_create, btn_multi, btn_list)
    return markup


def get_folder_actions_keyboard(folder_name):
    markup = types.InlineKeyboardMarkup()
    rename_btn = types.InlineKeyboardButton("✏️ Переименовать", callback_data=f'rename:{folder_name}')
    delete_btn = types.InlineKeyboardButton("🗑️ Удалить", callback_data=f'delete:{folder_name}')
    edit_btn = types.InlineKeyboardButton("📄 Редактировать .txt", callback_data=f'edit:{folder_name}')
    markup.add(rename_btn, delete_btn, edit_btn)
    return markup


def get_multi_choice_keyboard():
    markup = types.InlineKeyboardMarkup()
    same_btn = types.InlineKeyboardButton("🔢 Общее имя + номер", callback_data="same_name")
    diff_btn = types.InlineKeyboardButton("🏷️ Уникальные названия", callback_data="diff_names")
    markup.add(same_btn, diff_btn)
    return markup


# --- ОБРАБОТЧИКИ ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "👋 Добро пожаловать! Выберите действие:",
        reply_markup=get_main_keyboard()
    )


@bot.message_handler(func=lambda msg: msg.text == "📁 Создать папку")
def handle_create_folder(message):
    user_states[message.chat.id] = {'action': 'create_folder'}
    bot.send_message(message.chat.id, "Введите имя новой папки:")


@bot.message_handler(func=lambda msg: msg.text == "➕ Множественное создание")
def handle_multi_create(message):
    user_states[message.chat.id] = {'action': 'multi_choose'}
    bot.send_message(message.chat.id, "Выберите способ создания:", reply_markup=get_multi_choice_keyboard())


@bot.message_handler(func=lambda msg: msg.text == "🔍 Просмотр файловой системы")
def handle_list_files(message):
    folders, _ = logic.list_files_and_folders()
    if folders:
        bot.send_message(message.chat.id, "📂 Список папок:")
        for folder in folders:
            bot.send_message(
                message.chat.id,
                f"📁 {folder}",
                reply_markup=get_folder_actions_keyboard(folder)
            )
    else:
        bot.send_message(message.chat.id, "❌ Папок пока нет.")


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    data = call.data
    chat_id = call.message.chat.id

    state = user_states.get(chat_id)

    if data == "same_name":
        if state and state['action'] == 'multi_choose':
            user_states[chat_id] = {'action': 'multi_same'}
            bot.send_message(chat_id, "🔢 Введите количество папок и базовое имя через пробел:\nПример: 3 папка")

    elif data == "diff_names":
        if state and state['action'] == 'multi_choose':
            user_states[chat_id] = {'action': 'multi_diff', 'step': 'count'}
            bot.send_message(chat_id, "🔢 Введите количество папок:")

    elif data.startswith('rename:'):
        folder = data.split(':', 1)[1]
        user_states[chat_id] = {'action': 'rename_folder', 'old_name': folder}
        bot.send_message(chat_id, f"✏️ Введите новое имя для папки '{folder}':")

    elif data.startswith('delete:'):
        folder = data.split(':', 1)[1]
        result = logic.delete_folder(folder)
        bot.send_message(chat_id, result)

    elif data.startswith('edit:'):
        folder = data.split(':', 1)[1]
        user_states[chat_id] = {'action': 'edit_multi_file', 'folder': folder, 'step': 'count'}
        bot.send_message(chat_id, "🔢 Введите количество файлов:")


@bot.message_handler(func=lambda message: message.chat.id in user_states)
def handle_user_input(message):
    chat_id = message.chat.id
    state = user_states.get(chat_id)

    if state['action'] == 'create_folder':
        result = logic.create_folder(message.text.strip())
        bot.send_message(chat_id, result)
        del user_states[chat_id]

    elif state['action'] == 'rename_folder':
        new_name = message.text.strip()
        result = logic.rename_folder(state['old_name'], new_name)
        bot.send_message(chat_id, result)
        del user_states[chat_id]

    elif state['action'] == 'multi_same':
        parts = message.text.strip().split()
        if len(parts) < 2:
            bot.send_message(chat_id, "❗ Неверный формат. Пример: 3 папка")
            return
        try:
            count = int(parts[0])
            base_name = " ".join(parts[1:])
            result = logic.create_multiple_folders(count, base_name)
            bot.send_message(chat_id, result)
            del user_states[chat_id]
        except ValueError:
            bot.send_message(chat_id, "❗ Первое значение должно быть числом.")

    elif state['action'] == 'multi_diff':
        step = state['step']
        if step == 'count':
            try:
                count = int(message.text.strip())
                state['count'] = count
                state['step'] = 'names'
                state['names'] = []
                bot.send_message(chat_id, f"🔖 Введите название для первой из {count} папок:")
            except ValueError:
                bot.send_message(chat_id, "❗ Введите число.")
        elif step == 'names':
            state['names'].append(message.text.strip())
            if len(state['names']) < state['count']:
                bot.send_message(chat_id, f"🔖 Введите название для {len(state['names']) + 1}-й папки:")
            else:
                result = logic.create_multiple_folders(None, None, state['names'])
                bot.send_message(chat_id, result)
                del user_states[chat_id]

    elif state['action'] == 'edit_multi_file':
        step = state['step']
        if step == 'count':
            try:
                count = int(message.text.strip())
                state['count'] = count
                state['step'] = 'type'
                bot.send_message(chat_id, "Выберите способ создания файлов:", reply_markup=get_multi_choice_keyboard())
            except ValueError:
                bot.send_message(chat_id, "❗ Введите число.")
        elif step == 'type':
            folder = state['folder']
            count = state['count']
            if message.text.strip() == "same_name":
                state['step'] = 'base_name'
                bot.send_message(chat_id, "Введите базовое имя для файлов:")
            elif message.text.strip() == "diff_names":
                state['step'] = 'file_names'
                state['file_names'] = []
                bot.send_message(chat_id, f"Введите имя для первого из {count} файлов:")
        elif step == 'base_name':
            base_name = message.text.strip()
            folder = state['folder']
            result = logic.create_multiple_files(folder, state['count'], base_name)
            bot.send_message(chat_id, result)
            del user_states[chat_id]
        elif step == 'file_names':
            folder = state['folder']
            state['file_names'].append(message.text.strip())
            if len(state['file_names']) < state['count']:
                bot.send_message(chat_id, f"Введите имя для {len(state['file_names']) + 1}-го файла:")
            else:
                result = logic.create_multiple_files(folder, None, None, state['file_names'])
                bot.send_message(chat_id, result)
                del user_states[chat_id]


# --- ЗАПУСК БОТА ---
if __name__ == '__main__':
    print("Бот запущен...")
    bot.polling(none_stop=True)
