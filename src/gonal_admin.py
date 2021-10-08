import configparser

import telebot

from src import gonal_const as const

config = configparser.ConfigParser()
config.read("settings.ini")
TOKEN = config["settings"]["token"]
get_id = config["settings"]["admin_id"]
COMMENT_PAY = config["settings"]["comment_pay"]
ADMIN_ID = []

if "," in get_id:
    get_id = get_id.split(",")
    for a in get_id:
        ADMIN_ID.append(str(a))
else:
    try:
        ADMIN_ID = [str(get_id)]
    except ValueError:
        ADMIN_ID = [0]
        print("Не указан Admin_ID")

admin_keyboard = telebot.types.ReplyKeyboardMarkup(True)
admin_keyboard.row(const.BUY, const.FAQ)
admin_keyboard.row(const.ITEMS_WORK, const.WORK_PAY)
admin_keyboard.row(const.STAT)
admin_keyboard.row(const.REVIEW)
admin_keyboard.row(const.OTHER)

user_keyboard = telebot.types.ReplyKeyboardMarkup(True)
user_keyboard.row(const.BUY, const.FAQ)
user_keyboard.row(const.REVIEW)


user_methods = [
    "main_menu", "select_category",
    "select_subcat", "selected_item",
    "your_count", "select_pay", "buy_item", "check_pay",
    "support_user"
]

admin_methods = [
    "category", "sub_cat_add", "new_subcategory", "subitem_add", "add_item",
    "!del_item", "del_item", "category_del", "!del_cat", "del_cat", "!del_subcat", "del_subcat",
    "all_cat_edit", "cat_edit", "subcat_edit", "item_edit",
    "edit_name", "edit_desc", "edit_price", "get_data", "select_data", "edit_data", "delete_data", "add_item_data",
    "select_support", "ans_sup", "del_sup", "edit_supmes",
    "get_report", "report",
    "payment", "check", "edit",
    "get_support"
]


def is_admin(user):
    return str(user) in ADMIN_ID
