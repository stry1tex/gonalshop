import telebot

import gonal_database as database
from src import gonal_booking as booking
from src import gonal_const as const

CLOSE_BTN = telebot.types.InlineKeyboardButton(text=const.CLOSE, callback_data="cancel")


# клавиатура с категориями
def get_categories(method):
    keyboard = telebot.types.InlineKeyboardMarkup()
    categories = database.get_categories()

    length = len(categories)

    b = True
    if length > 0:
        for i in range(length):
            keyboard.add(telebot.types.InlineKeyboardButton(
                text=str(categories[i][1]), callback_data=f"{method}={str(categories[i][0])}"))
    else:
        b = False

    return keyboard, b


# клавиатура с подкатегориями
def get_subcategories(method, category):
    keyboard = telebot.types.InlineKeyboardMarkup()
    subcat = database.get_subcategories(category)

    count = False

    for i in range(len(subcat)):
        on_click = f"{method}={str(subcat[i][0])}|{str(category)}"
        keyboard.add(telebot.types.InlineKeyboardButton(text=subcat[i][1],
                                                        callback_data=on_click))
        count = True

    return keyboard, count


# заполнить клавиатуру товарами
def get_items(keyboard, category, sub_category, method):
    items = database.get_items(category, sub_category)
    count = False

    for i in range(len(items)):
        item_id = str(items[i][0])
        item_name = str(items[i][1])
        item_price = str(items[i][3])
        item_count = items[i][6] - booking.get_booking(item_name)

        if method != "!del_item":
            if item_count == "file" or method == "item_edit":
                item_str = f"{item_name} {item_price}руб."
            else:
                item_str = f"{item_name} {item_price}руб. ({item_count} шт.)"
        else:
            item_str = f"{item_name}"

        keyboard.add(
            telebot.types.InlineKeyboardButton(text=item_str, callback_data=f"{method}={item_id}"))
        count = True

    return keyboard, count


# генерация клавиатуры с оплатой и проверкой
def create_check_buttons(method_url, method_check, method_back):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton(text="💳 Оплатить", url=method_url))
    keyboard.add(telebot.types.InlineKeyboardButton(text="🔄 Проверка оплаты", callback_data=method_check))
    keyboard.row(telebot.types.InlineKeyboardButton(text=const.BACK, callback_data=method_back),
                 CLOSE_BTN)

    return keyboard


# Фабрика для страничной клавиатуры
class PageKeyboardFabric:
    def __init__(self, data, text_type, click_method, list_method, return_method):
        self.item = 0

        self.data = data
        self.text_type = text_type
        self.click = click_method

        self.list_method = list_method
        self.return_method = return_method

    def get_click_method(self):
        if self.click != "report":
            return f"{self.click}={self.data[self.item][0]}"
        else:
            return f"{self.click}={self.data[self.item]}|{self.item // 10}"

    def get_btn_text(self):
        if self.text_type == "item_data":
            return f"{self.data[self.item][6]}"
        elif self.text_type == "appeals":
            return f"{self.data[self.item][1]} : {self.data[self.item][3]}"
        elif self.text_type == "stat":
            return f"{self.data[self.item][0]}"
        elif self.text_type == "stat_date":
            return f"{self.data[self.item]}"

    def create_keyboard(self, page):
        keyboard = telebot.types.InlineKeyboardMarkup()

        self.item = int(page)
        next_page = self.item + 10

        while self.item < next_page and self.item < len(self.data):
            desc = self.get_btn_text()

            keyboard.add(telebot.types.InlineKeyboardButton(
                text=desc, callback_data=self.get_click_method()
            ))
            self.item += 1

        btn_list = []
        if next_page < len(self.data):
            btn_list.append(telebot.types.InlineKeyboardButton(text=const.NEXT,
                                                               callback_data=f"{self.list_method}{next_page}"))
        if int(page) >= 10:
            prev_page = int(page) - 10
            btn_list.append(telebot.types.InlineKeyboardButton(text=const.BACK,
                                                               callback_data=f"{self.list_method}{prev_page}"))

        if len(btn_list) == 2:
            keyboard.row(btn_list[1], btn_list[0])
        elif len(btn_list) == 1:
            keyboard.row(btn_list[0])

        if self.text_type != "appeals" and self.text_type != "stat" and self.text_type != "stat_date":
            btn_back = telebot.types.InlineKeyboardButton(text=const.RETURN,
                                                          callback_data=f"{self.return_method}")
            keyboard.row(btn_back, CLOSE_BTN)
        else:
            keyboard.row(CLOSE_BTN)

        return keyboard
