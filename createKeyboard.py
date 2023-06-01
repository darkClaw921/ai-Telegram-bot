import telebot

def create_keyboard_is_row(rows: list):
    keyboard = telebot.types.ReplyKeyboardMarkup(True)

    for row in rows:
        keyboard.row(row)
    return keyboard


def create_menu_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('/addmodel')
    keyboard.row('/addpromt')
    keyboard.row('/context')
    keyboard.row('/model') 
    keyboard.row('/promt')
    return keyboard