from src import gonal_const as const
from src import gonal_keyboards as keyboards
import telebot
import gonal_database as database


class ItemCreator:
    def __init__(self):
        self.name = None
        self.desc = ""
        self.price = 0
        self.data = []
        self.category = ""
        self.subcategory = ""

    def clear(self):
        self.name = ""
        self.desc = ""
        self.price = 0
        self.data = []
        self.category = ""
        self.subcategory = ""

    def input_item(self):
        for i in range(len(self.data)):
            if const.not_const(self.data[i]) is False:
                self.data.pop(i)

        database.input_item(self.name, self.desc, self.price, self.subcategory, self.category, self.data)

    def input_file(self):
        database.input_item_file(self.name, self.desc, self.price, self.subcategory, self.category, self.data)


class ItemEditor:
    def __init__(self, id):
        self.id = ""
        self.name = None
        self.desc = ""
        self.price = ""
        self.category = ""
        self.subcategory = ""
        self.count = ""
        self.data = ""

        self.id_edit = ""

        self.last_page = ""
        if id != -1:
            self.create_from_data(database.get_item_by_id(id))

        self.fabric = None
        self.create_fabric()
        self.load_file = False

    def create_from_data(self, list):
        self.id = list[0]
        self.name = list[1]
        self.desc = list[2]
        self.price = list[3]
        self.category = list[4]
        self.subcategory = list[5]
        self.count = list[6]
        self.refresh_data()

    def refresh_data(self):
        self.data = database.get_all_item(self.name)

    def create_fabric(self):
        self.fabric = keyboards.PageKeyboardFabric(self.data,
                                                   "item_data",
                                                   "select_data",
                                                   "get_data=",
                                                   f"item_edit={self.id}")

    def get_text(self):
        return f"▫ Название: {self.name}\n" \
               f"▫ Описание: {self.desc}\n" \
               f"▫ Цена: {self.price} руб.\n" \
               f"▫ Количество: {self.count} шт."

    def get_keyboard(self):
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(
            telebot.types.InlineKeyboardButton(text=const.EDIT_NAME, callback_data="edit_name"))
        keyboard.add(
            telebot.types.InlineKeyboardButton(text=const.EDIT_DESC, callback_data="edit_desc"))
        keyboard.add(
            telebot.types.InlineKeyboardButton(text=const.EDIT_PRICE, callback_data="edit_price"))
        keyboard.add(
            telebot.types.InlineKeyboardButton(text=const.EDIT_DATA, callback_data="get_data=0"))
        keyboard.add(
            telebot.types.InlineKeyboardButton(text=const.ADD_ITEM, callback_data="add_item_data"))
        keyboard.add(
            telebot.types.InlineKeyboardButton(text=const.DELETE_ITEM,
                                               callback_data=f"!del_item={self.id}"))

        if self.subcategory == "":
            method = f"cat_edit={self.category}"
        else:
            method = f"subcat_edit={self.subcategory}|{self.category}"

        keyboard.row(telebot.types.InlineKeyboardButton(text=const.BACK, callback_data=method),
                     keyboards.CLOSE_BTN)

        return keyboard

    def update_name(self, new_name):
        self.name = new_name
        database.edit_item_name(self.id, new_name)

    def update_desc(self, new_desc):
        self.desc = new_desc
        database.edit_item_desc(self.id, new_desc)

    def update_price(self, new_price):
        self.price = new_price
        database.edit_item_price(self.id, new_price)

    def get_item_all_data(self, page):
        self.last_page = page
        keyboard = self.fabric.create_keyboard(page)

        return keyboard

    def select_data(self, id):
        self.id_edit = id
        item = database.get_item_from_id(id)
        msg = f"◽ ID:{item[0]}\n{item[6]}"
        keyboard = telebot.types.InlineKeyboardMarkup()
        btn_edit = telebot.types.InlineKeyboardButton(text="✏ Редактировать",
                                                      callback_data=f"edit_data")
        btn_delete = telebot.types.InlineKeyboardButton(text="🗑 Удалить",
                                                        callback_data="delete_data")
        keyboard.row(btn_edit, btn_delete)

        btn_back = telebot.types.InlineKeyboardButton(text=const.RETURN,
                                                      callback_data=f"get_data={self.last_page}")
        keyboard.row(btn_back, keyboards.CLOSE_BTN)

        return msg, keyboard

    def update_data(self, new_data):
        database.edit_item_data(self.id_edit, new_data)
        self.refresh_data()
        self.fabric.data = self.data

    def delete_data(self):
        database.delete_item_data(self.id_edit)
        self.refresh_data()
        self.fabric.data = self.data

    def add_data(self, data_list):
        database.input_item(self.name, self.desc, self.price, self.subcategory, self.category, data_list)
        self.refresh_data()
        self.fabric.data = self.data

    def add_file(self, file_path):
        database.input_item_file(self.name, self.desc, self.price, self.subcategory, self.category, file_path)

class CategoryCreator:
    def __init__(self):
        self.category = ""
        self.subcategory = ""

    def clear(self):
        self.category = ""
        self.subcategory = ""

    def create_category(self):
        category_list = self.category.split("\n")
        count = 0

        for i in range(len(category_list)):
            if not database.get_category_name(category_list[i]) and const.not_const(category_list[i]):
                database.input_category(category_list[i])
                count += 1

        self.clear()
        return count

    def create_subcategory(self):
        subcategory_list = self.subcategory.split("\n")
        count = 0

        for i in range(len(subcategory_list)):
            if not database.get_subcat_name(subcategory_list[i]) and const.not_const(subcategory_list[i]):
                database.input_subcategory(subcategory_list[i], self.category)

                count += 1

        self.clear()
        return count
