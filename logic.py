# logic.py
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Запрещенные символы Windows
INVALID_CHARS = r'[<>:"/\\|?*]'
INVALID_NAMES = ["CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5",
                 "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3", "LPT4", "LPT5",
                 "LPT6", "LPT7", "LPT8", "LPT9"]


def is_valid_name(name):
    name = name.strip()
    if re.search(INVALID_CHARS, name):
        return False, f"❌ Имя содержит запрещённые символы (например: < > : \" / \\ | ? *)"
    if name.upper() in INVALID_NAMES:
        return False, f"❌ Имя '{name}' зарезервировано системой Windows."
    if name.endswith(" ") or name.endswith("."):
        return False, f"❌ Имя не должно заканчиваться пробелом или точкой."
    if not name:
        return False, f"❌ Имя не может быть пустым."
    return True, ""


def create_folder(folder_name):
    valid, msg = is_valid_name(folder_name)
    if not valid:
        return msg

    folder_path = os.path.join(BASE_DIR, folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        return f"✅ Папка '{folder_name}' успешно создана."
    else:
        return f"❌ Папка '{folder_name}' уже существует."


def rename_folder(old_name, new_name):
    valid, msg = is_valid_name(new_name)
    if not valid:
        return msg

    old_path = os.path.join(BASE_DIR, old_name)
    new_path = os.path.join(BASE_DIR, new_name)

    if not os.path.exists(old_path):
        return f"❌ Папка '{old_name}' не найдена."

    if os.path.exists(new_path):
        return f"❌ Папка '{new_name}' уже существует."

    os.rename(old_path, new_path)
    return f"🔄 Папка '{old_name}' переименована в '{new_name}'."


def delete_folder(folder_name):
    folder_path = os.path.join(BASE_DIR, folder_name)

    if not os.path.exists(folder_path):
        return f"❌ Папка '{folder_name}' не найдена."

    try:
        os.rmdir(folder_path)  # Только для пустых папок
        return f"🗑️ Папка '{folder_name}' удалена (была пустой)."
    except OSError:
        shutil.rmtree(folder_path)
        return f"💥 Папка '{folder_name}' и всё её содержимое удалены."


def list_files_and_folders():
    items = os.listdir(BASE_DIR)
    folders = [item for item in items if os.path.isdir(os.path.join(BASE_DIR, item))]
    files = [item for item in items if os.path.isfile(os.path.join(BASE_DIR, item))]
    return folders, files


def create_or_edit_file(folder_name, file_name, content=None):
    folder_path = os.path.join(BASE_DIR, folder_name)
    file_path = os.path.join(folder_path, file_name)

    if not os.path.exists(folder_path):
        return f"❌ Папка '{folder_name}' не найдена."

    if content is None:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return "📄 Текст из файла:\n\n" + f.read()
        else:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("")
            return "🆕 Файл создан. Вы можете начать его редактировать."
    else:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return "💾 Файл успешно сохранён."


def create_multiple_folders(count, base_name, unique_names=None):
    results = []
    if unique_names:
        for i, name in enumerate(unique_names):
            result = create_folder(name)
            results.append(result)
    else:
        for i in range(1, count + 1):
            name = f"{base_name}_{i}"
            result = create_folder(name)
            results.append(result)
    return "\n".join(results)


def create_multiple_files(folder_name, count, base_name, unique_names=None):
    results = []
    if unique_names:
        for name in unique_names:
            if not name.lower().endswith('.txt'):
                name += '.txt'
            result = create_or_edit_file(folder_name, name, " ")
            results.append(result)
    else:
        for i in range(1, count + 1):
            name = f"{base_name}_{i}.txt"
            result = create_or_edit_file(folder_name, name, " ")
            results.append(result)
    return "\n".join(results)