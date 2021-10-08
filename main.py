# -*- coding: utf-8 -*-
import os
import sys
import time
from datetime import datetime

import telebot
from telebot.util import async_dec

import gonal_database as database
import gonal_payment as payment
import gonal_strings as string_help
from src import gonal_admin as admin
from src import gonal_booking as booking
from src import gonal_item as item_menu
from src import gonal_keyboards as keyboards
from src import gonal_stat as statistics
from src import gonal_support as support
from src.gonal_const import *

bot = telebot.AsyncTeleBot(admin.TOKEN, parse_mode="MARKDOWN")

admin_keyboard = admin.admin_keyboard
user_keyboard = admin.user_keyboard

database.open_db()

qiwi = payment.Qiwi()
yoomoney = payment.YooMoney()

support = support.Support()
stat = statistics.Stat()

global item_creator
item_creator = item_menu.ItemCreator()
global item_editor
item_editor = item_menu.ItemEditor(-1)


@bot.message_handler(commands=['start'])
def start_message(message):
    if database.input_user(message.chat.id) is True:
        msg = "Добро пожаловать! Если не появились кнопки, напишите /start."
    else:
        msg = f"С возвращением, @{message.from_user.username}!"

    if admin.is_admin(message.from_user.id):
        bot.send_message(message.chat.id, msg, reply_markup=admin_keyboard, parse_mode="HTML")
    else:
        bot.send_message(message.chat.id, msg, reply_markup=user_keyboard, parse_mode="HTML")




# Купить
@bot.message_handler(regexp=BUY)
def buy_message(message):
    keyboard, count = keyboards.get_categories("select_category")
    keyboard.add(keyboards.CLOSE_BTN)
    if count:
        bot.send_message(message.from_user.id, "📂 Доступные категории:", reply_markup=keyboard)
    else:
        bot.send_message(message.from_user.id, "😔 В данный момент товары отсутствуют")


# FAQ
@bot.message_handler(regexp=FAQ)
def faq_message(message):
    bot.send_message(message.chat.id, database.get_faq(), parse_mode="HTML")





# Написать тикет в поддержку
@bot.message_handler(regexp=REVIEW)
def review_message(message):
    if admin.is_admin(message.from_user.id):
        keyboard = telebot.types.ReplyKeyboardMarkup(True)
        keyboard.row(SUPPORT, SUPPORT_HISTORY)
        keyboard.row(SUPPORT_MES)
        keyboard.row(BACK)
        bot.send_message(message.chat.id, REVIEW, reply_markup=keyboard)
    else:
        bot.send_message(message.from_user.id, database.get_support_main_mes(), parse_mode="HTML")
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton(text="❓ Вопрос",
                                                        callback_data="support_user=❓ Вопрос"))
        keyboard.add(telebot.types.InlineKeyboardButton(text="💳 Оплата",
                                                        callback_data="support_user=💳 Оплата"))
        keyboard.add(telebot.types.InlineKeyboardButton(text="📚 Товары",
                                                        callback_data="support_user=📚 Товары"))
        keyboard.add(telebot.types.InlineKeyboardButton(text="📝 Прочее",
                                                        callback_data="support_user=📝 Прочее"))
        keyboard.add(keyboards.CLOSE_BTN)
        bot.send_message(message.from_user.id, "📝 Выберите категорию обращения", reply_markup=keyboard)


# Админ панель
# Прочее
@bot.message_handler(regexp=OTHER, func=lambda msg: admin.is_admin(msg.from_user.id))
def other_message(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row(SENDING)
    keyboard.row(EDIT_FAQ)
    keyboard.row(BACK)
    bot.send_message(message.chat.id, OTHER, reply_markup=keyboard)


# Рассылки
@bot.message_handler(regexp=SENDING, func=lambda msg: admin.is_admin(msg.from_user.id))
def sending_message(message):
    bot.send_message(message.chat.id, "📝 Введите текст рассылки")
    bot.register_next_step_handler(message, create_sending)


# Обращения в поддержку без ответа
@bot.message_handler(regexp=SUPPORT, func=lambda msg: admin.is_admin(msg.from_user.id))
def support_message(message):
    support.generate_sup_mes(False)
    keyboard = support.get_support_msg(0)
    bot.send_message(message.from_user.id, "👨‍💻 История запросов", reply_markup=keyboard)


# История запросов
@bot.message_handler(regexp=SUPPORT_HISTORY, func=lambda msg: admin.is_admin(msg.from_user.id))
def support_history_message(message):
    support.generate_sup_mes(True)
    keyboard = support.get_support_msg(0)
    bot.send_message(message.from_user.id, "👨‍💻 История запросов", reply_markup=keyboard)


# Описание поддержки
@bot.message_handler(regexp=SUPPORT_MES, func=lambda msg: admin.is_admin(msg.from_user.id))
def support_history_message(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton(text="✏ Редактировать",
                                                    callback_data="edit_supmes"))
    bot.send_message(message.from_user.id, database.get_support_main_mes(), reply_markup=keyboard)


# Редактирование FAQ
@bot.message_handler(regexp=EDIT_FAQ, func=lambda msg: admin.is_admin(msg.from_user.id))
def edit_faq_message(message):
    bot.send_message(message.from_user.id, "✒ Введите новый текст FAQ")
    bot.register_next_step_handler(message, edit_faq)


# Работа с товаром
@bot.message_handler(regexp=ITEMS_WORK, func=lambda msg: admin.is_admin(msg.from_user.id))
def items_word_message(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row(ADD_ITEM, EDIT_ITEM)
    keyboard.row(ADD_CATEGORY, DELETE_CATEGORY)
    keyboard.row(BACK)
    bot.send_message(message.chat.id, ITEMS_WORK, reply_markup=keyboard)


# Добавить товар
@bot.message_handler(regexp=ADD_ITEM, func=lambda msg: admin.is_admin(msg.from_user.id))
def add_item_message(message):
    keyboard, b = keyboards.get_categories("category")
    keyboard.add(keyboards.CLOSE_BTN)

    if b:
        bot.send_message(message.chat.id, "📚 Выберите категорию товара", reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "😔 Нет доступных категорий")


# Управление товарами
@bot.message_handler(regexp=EDIT_ITEM, func=lambda msg: admin.is_admin(msg.from_user.id))
def edit_item_name(message):
    keyboard, b = keyboards.get_categories("cat_edit")
    keyboard.add(keyboards.CLOSE_BTN)

    if b:
        bot.send_message(message.chat.id, "📚 Выберите категорию товара", reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "😔 Нет доступных категорий")


# Добавить категорию
@bot.message_handler(regexp=ADD_CATEGORY, func=lambda msg: admin.is_admin(msg.from_user.id))
def add_category_message(message):
    keyboard, b = keyboards.get_categories("sub_cat_add")

    keyboard.add(telebot.types.InlineKeyboardButton(text="📝 Добавить новую категорию",
                                                    callback_data="category=new_category"))
    keyboard.add(keyboards.CLOSE_BTN)
    bot.send_message(message.chat.id, "📂 Существующие категории \n"
                                      "📁 Для добавления подкатегории *нажмите на нужную категорию*",
                     reply_markup=keyboard)


# Удалить категорию
@bot.message_handler(regexp=DELETE_CATEGORY, func=lambda msg: admin.is_admin(msg.from_user.id))
def delete_category_message(message):
    keyboard, b = keyboards.get_categories("category_del")
    keyboard.add(keyboards.CLOSE_BTN)
    if b:
        bot.send_message(message.chat.id, "📁 Выберите категорию", reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "😔 Нет доступных категорий")


# Работа с кошельками
@bot.message_handler(regexp=WORK_PAY, func=lambda msg: admin.is_admin(msg.from_user.id))
def work_pay_message(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton(text="🥝 QIWI", callback_data="payment=qiwi"))
    keyboard.add(telebot.types.InlineKeyboardButton(text="💳 YooMoney", callback_data="payment=yoomoney"))
    keyboard.add(keyboards.CLOSE_BTN)

    bot.send_message(message.chat.id, "💳 Выберите кошелек", reply_markup=keyboard)


# Статистика
@bot.message_handler(regexp=STAT, func=lambda msg: admin.is_admin(msg.from_user.id))
def stat_message(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row(REPORT, GENERAL)
    keyboard.row(BACK)
    bot.send_message(message.chat.id, STAT, reply_markup=keyboard)


# Отчеты
@bot.message_handler(regexp=REPORT, func=lambda msg: admin.is_admin(msg.from_user.id))
def report_message(message):
    stat.create_date_list()
    keyboard = stat.get_stat_page(0)

    bot.send_message(message.from_user.id, "📆 Выберите дату отчета", reply_markup=keyboard)


# Общая статистика
@bot.message_handler(regexp=GENERAL, func=lambda msg: admin.is_admin(msg.from_user.id))
def general_stat_message(message):
    keyboard = telebot.types.InlineKeyboardMarkup()

    keyboard.add(keyboards.CLOSE_BTN)
    bot.send_message(message.from_user.id, stat.get_all_stat(), reply_markup=keyboard)


# Назад
@bot.message_handler(regexp=BACK)
def back_message(message):
    if admin.is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "🔹 Главное меню 🔹", reply_markup=admin_keyboard)
    else:
        bot.send_message(message.chat.id, "🔹 Главное меню 🔹", reply_markup=user_keyboard)


# Неизвестная команда
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if admin.is_admin(message.from_user.id):
        bot.send_message(message.from_user.id, "❗ Неизвестная команда! Введите /start",
                         reply_markup=admin_keyboard)
    else:
        bot.send_message(message.from_user.id, "❗ Неизвестная команда! Введите /start",
                         reply_markup=user_keyboard)


# отправка сообщений админам
@async_dec()
def send_admin_mes(message):
    for i in range(len(admin.ADMIN_ID)):
        bot.send_message(admin.ADMIN_ID[i], message, parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data.split("=")[0] in admin.user_methods)
def user_callback(call):
    call_data = call.data.split("=")

    # Главное меню
    if call_data[0] == "main_menu":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        keyboard, count = keyboards.get_categories("select_category")
        keyboard.add(keyboards.CLOSE_BTN)
        if count:
            bot.send_message(call.message.chat.id, "📂 Доступные категории", reply_markup=keyboard)
        else:
            bot.send_message(call.message.chat.id, "😔 В данный момент товары отсутствуют")

    # Выбранная категория
    elif call_data[0] == "select_category":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        keyboard, count = keyboards.get_subcategories("select_subcat", call_data[1])
        keyboard, items = keyboards.get_items(keyboard, call_data[1], "", "selected_item")

        keyboard.row(telebot.types.InlineKeyboardButton(text=BACK, callback_data="main_menu"),
                     keyboards.CLOSE_BTN)

        if count is True or items is True:
            bot.send_message(call.message.chat.id, "📙 Доступные товары", reply_markup=keyboard)
        else:
            bot.send_message(call.message.chat.id,
                             "😔 В данный момент товары отсутствуют", reply_markup=keyboard)

    # Подкатегория
    elif call_data[0] == "select_subcat":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        categories = call_data[1].split("|")

        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard, count = keyboards.get_items(keyboard, categories[1], categories[0], "selected_item")

        keyboard.add(telebot.types.InlineKeyboardButton(text=BACK,
                                                        callback_data=f"select_category={str(categories[1])}"),
                     keyboards.CLOSE_BTN)
        if count:
            bot.send_message(call.message.chat.id, "📙 Доступные товары", reply_markup=keyboard)
        else:
            bot.send_message(call.message.chat.id,
                             "😔 В данный момент товары отсутствуют", reply_markup=keyboard)

    # Выбранный предмет
    elif call_data[0] == "selected_item":
        bot.delete_message(call.message.chat.id, call.message.message_id)

        item = database.get_item_by_id(call_data[1])

        item_name = str(item[1])
        item_desc = str(item[2])
        item_price = str(item[3])
        item_category = str(item[4])
        item_subcategory = str(item[5])
        item_count = item[6] - booking.get_booking(item_name)

        keyboard = telebot.types.InlineKeyboardMarkup(row_width=5)

        if str(item[5]) == "":
            method_back = f"select_category={item_category}"
        else:
            method_back = f"select_subcat={item_subcategory}|{item_category}"

        method_buy = f"select_pay={str(call_data[1])}|"

        if item[6] != 0:
            btn_list = []

            i = 0
            while i < 10 and i < item_count:
                i += 1
                count_str = str(i)
                btn_list.append(telebot.types.InlineKeyboardButton(text=f"{count_str} шт.",
                                                                   callback_data=f"{method_buy}{count_str}"))

            keyboard.add(*btn_list)
            if i < item_count:
                keyboard.row(telebot.types.InlineKeyboardButton(text="🛒 Свое значение",
                                                                callback_data=f"your_count={str(call_data[1])}|{item_count}"))

            msg = string_help.get_info_message(item_name, item_desc, item_price, item_count)
        else:
            msg = "😔 Извините, но данного товара сейчас нет в наличии"

        keyboard.row(telebot.types.InlineKeyboardButton(text=BACK, callback_data=method_back), keyboards.CLOSE_BTN)

        bot.send_message(call.message.chat.id, msg,
                         reply_markup=keyboard)

    # свое значение
    elif call_data[0] == "your_count":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        temp = call_data[1].split("|")
        limit = int(temp[1])
        if limit > 15:
            limit = 15

        bot.send_message(call.message.chat.id, f"🛒 Введите свое значение для товара:\n"
                                               f"Минимальное: 1\n"
                                               f"Маскимальное: {limit}")
        bot.register_next_step_handler(call.message, check_count, temp[0], limit)

    # выбор оплаты
    elif call_data[0] == "select_pay":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        select_pay(call.message, call_data[1])

    # Покупка
    elif call_data[0] == "buy_item":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        buy_item(call.message, call_data[1])

    # Проверка оплаты
    elif call_data[0] == "check_pay":
        temp_data = call_data[1].split("|")
        pay_method = temp_data[0]
        comment = temp_data[1]
        count_buy = int(temp_data[3])

        item = database.get_item_by_id(temp_data[2])

        item_name = item[1]
        item_price = item[3]

        amount = int(item_price) * count_buy

        is_buy_item = False

        if pay_method == "qiwi":
            is_buy_item = qiwi.payment_ver(comment, amount)
        elif pay_method == "yoo":
            is_buy_item = yoomoney.payment_ver(comment, amount)

        if is_buy_item:
            item_data = []

            for i in range(count_buy):
                item_id = database.get_item_id(item_name)
                if item_id == -1:
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                    message = "❗ Произошла ошибка при выдаче товара ❗\n" \
                              "Возможно, этот товар уже успели купить и он закончился❗\n" \
                              "Вам напишет администратор магазина"

                    bot.send_message(call.message.chat.id, message)
                    message = "<b>❗ Не прошла покупка ❗</b>\n" \
                              f"🔹 Пользователь: @{call.message.chat.username}\n" \
                              f"🔹 Товар: {item_name}\n" \
                              f"🔹 Количество: {count_buy}\n" \
                              f"🔹 Сумма покупки: {amount}\n" \
                              f"🔹 Комментарий к оплате: {comment}"
                    send_admin_mes(message)
                    continue

                item_data_str = f"{database.get_item_data(item_id)}"
                item_data.append(item_data_str)

                date = datetime.now()
                day = date.day
                month = date.month
                year = date.year
                format_date = f"{day}/{month}/{year}"

                database.input_info_buy(call.message.chat.id, item_name, item_id,
                                        comment, item_price, item_data_str, format_date)

            msg = string_help.get_sold_message(call.message.chat.username, item_name, amount)

            bot.delete_message(call.message.chat.id, call.message.message_id)

            format_data = ""
            for i in range(len(item_data)):
                temp_data = item_data[i]

                parse_data = temp_data[0:7]
                if parse_data == "[file]=":
                    split = temp_data.split(parse_data)
                    src = split[1]

                    bot.send_document(call.message.chat.id,
                                      open(src, "rb"),
                                      caption=f"✨ Поздравляем вас с приобретением {item_name} \n",
                                      parse_mode="HTML")
                else:
                    format_data += f"{item_data[i]}\n"

            bot.send_message(call.message.chat.id,
                             text=f"✨ Поздравляем вас с приобретением {item_name} \n"
                                  f"🎁 Данные товара:\n<b>{format_data}</b>", parse_mode="HTML")

            msg += f"\n🔹 Данные:\n{format_data}"

            send_admin_mes(msg)

            booking.del_booking(call.message.chat.id)
        else:
            bot.answer_callback_query(callback_query_id=call.id, show_alert=True,
                                      text="❗ Пополнение не найдено ❗\n Попробуйте еще раз")

    # Обращение в поддержку
    elif call_data[0] == "support_user":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "✏ Введите текст обращения")
        bot.register_next_step_handler(call.message, send_support, call_data[1])


@bot.callback_query_handler(func=lambda call: call.data.split("=")[0] in admin.admin_methods)
def admin_callback(call):
    call_data = call.data.split("=")

    bot.delete_message(call.message.chat.id, call.message.message_id)
    if admin.is_admin(call.message.chat.id) is False:
        bot.send_message(call.message.chat.id, "! У вас нет прав на выполение данной комадны !")
        return

    # # # # # # # # #
    # Админ Команды
    # Категории
    if call_data[0] == "category":
        global category_creator
        category_creator = item_menu.CategoryCreator()

        if call_data[1] == "new_category":
            bot.send_message(call.message.chat.id, "📁 Введите название категории\n*Одна категория - Одна строка*")
            bot.register_next_step_handler(call.message, new_category)
        else:
            item_creator.clear()
            item_creator.category = call_data[1]

            keyboard, b = keyboards.get_subcategories("subitem_add", call_data[1])

            keyboard.row(telebot.types.InlineKeyboardButton(text="📚 Добавить товар",
                                                            callback_data=f"add_item={call_data[1]}"),
                         keyboards.CLOSE_BTN)
            bot.send_message(call.message.chat.id,
                             "📕 Выберите подкатегорию для товара \nИли можете добавить его в данную категорию",
                             reply_markup=keyboard)

    # Добавление подкатегории
    elif call_data[0] == "sub_cat_add":
        keyboard = telebot.types.InlineKeyboardMarkup()
        list_sub = ""

        subcategory_list = database.get_subcategories(call_data[1])
        for i in range(len(subcategory_list)):
            list_sub += f"▪ {subcategory_list[i][1]}\n"

        keyboard.row(telebot.types.InlineKeyboardButton(
            text="📝 Добавить новую подкатегорию", callback_data=f"new_subcategory={call_data[1]}"),
            keyboards.CLOSE_BTN)

        bot.send_message(call.message.chat.id,
                         f"📂 Доступные подкатегории \n{list_sub}", reply_markup=keyboard)

    # Добавление подкатегории
    elif call_data[0] == "new_subcategory":
        category_creator.category = call_data[1]

        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "📁 Введите название подкатегории\n"
                                               "*Одна подкатегория - Одна строка*")
        bot.register_next_step_handler(call.message, new_subcategory)

    # Добавление товара
    # В подкатегорию
    elif call_data[0] == "subitem_add":
        item_creator.subcategory = call_data[1].split("|")[0]

        bot.send_message(call.message.chat.id, "📚 Введите название товара")
        bot.register_next_step_handler(call.message, add_item_name)

    # В категорию
    elif call_data[0] == "add_item":
        item_creator.subcategory = ""

        bot.send_message(call.message.chat.id, "📚 Введите название товара")
        bot.register_next_step_handler(call.message, add_item_name)

    # Редактирование товаров
    elif call_data[0] == "all_cat_edit":
        keyboard, b = keyboards.get_categories("cat_edit")
        keyboard.add(keyboards.CLOSE_BTN)
        if b:
            bot.send_message(call.message.chat.id, "📚 Выберите категорию товара", reply_markup=keyboard)
        else:
            bot.send_message(call.message.chat.id, "😔 Нет доступных категорий")

    elif call_data[0] == "cat_edit":
        keyboard, count = keyboards.get_subcategories("subcat_edit", call_data[1])
        keyboard, items = keyboards.get_items(keyboard, call_data[1], "", "item_edit")
        keyboard.row(telebot.types.InlineKeyboardButton(text=BACK, callback_data="all_cat_edit"),
                     keyboards.CLOSE_BTN)

        if count is True or items is True:
            bot.send_message(call.message.chat.id, "📙 Доступные товары", reply_markup=keyboard)
        else:
            bot.send_message(call.message.chat.id,
                             "😔 В данный момент товары отсутствуют", reply_markup=keyboard)

    elif call_data[0] == "subcat_edit":
        categories = call_data[1].split("|")

        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard, count = keyboards.get_items(keyboard, categories[1], categories[0], "item_edit")

        keyboard.row(telebot.types.InlineKeyboardButton(text=BACK,
                                                        callback_data=f"cat_edit={str(categories[1])}"),
                     keyboards.CLOSE_BTN)
        if count:
            bot.send_message(call.message.chat.id, "📙 Доступные товары", reply_markup=keyboard)
        else:
            bot.send_message(call.message.chat.id,
                             "😔 В данный момент товары отсутствуют", reply_markup=keyboard)

    # Редактирование товара
    elif call_data[0] == "item_edit":
        get_item_msg(call.message, call_data[1])

    elif call_data[0] == "edit_name":
        bot.send_message(call.message.chat.id, "📝 Введите имя")
        bot.register_next_step_handler(call.message, edit_name)

    elif call_data[0] == "edit_desc":
        bot.send_message(call.message.chat.id, "📝 Введите описание")
        bot.register_next_step_handler(call.message, edit_desc)

    elif call_data[0] == "edit_price":
        bot.send_message(call.message.chat.id, "📝 Введите цену")
        bot.register_next_step_handler(call.message, edit_price)

    elif call_data[0] == "get_data":
        keyboard = item_editor.get_item_all_data(call_data[1])
        bot.send_message(call.message.chat.id, "📙 Доступные товары", reply_markup=keyboard)

    elif call_data[0] == "select_data":
        get_item_data(call.message, call_data[1])

    elif call_data[0] == "edit_data":
        bot.send_message(call.message.chat.id, "📝 Введите данные")
        bot.register_next_step_handler(call.message, edit_data)

    elif call_data[0] == "delete_data":
        item_editor.delete_data()
        keyboard = item_editor.get_item_all_data(item_editor.last_page)
        bot.send_message(call.message.chat.id, "📙 Доступные товары", reply_markup=keyboard)

    elif call_data[0] == "add_item_data":
        bot.send_message(call.message.chat.id, "🔐 Введите данные товара \n*Один товар - Одна строка* \n"
                                               "💾 Или же загрузите архивы или файлы с товаром (до *10 штук*)\n"
                                               "❗ *Опасная функция*. Возможны выпадения бота при загрузке/продаже файлов. Данная функция еще в бета-тестировании❗")
        bot.register_next_step_handler(call.message, add_data)

    # Удаление выбранного товара
    elif call_data[0] == "!del_item":
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(
            telebot.types.InlineKeyboardButton(text=YES, callback_data=f"del_item={call_data[1]}"))
        keyboard.add(
            telebot.types.InlineKeyboardButton(text=NO, callback_data="cancel"))

        bot.send_message(call.message.chat.id, f"❓ Удалить товар ❓", reply_markup=keyboard)
    elif call_data[0] == "del_item":
        database.delete_item(call_data[1])
        bot.send_message(call.message.chat.id, f"❗ Товар удален ❗")

    # Удаление категории
    elif call_data[0] == "category_del":
        keyboard, b = keyboards.get_subcategories("!del_subcat", call_data[1])
        keyboard.add(telebot.types.InlineKeyboardButton(text="🚫 Удалить всю категорию",
                                                        callback_data=f"!del_cat={str(call_data[1])}"))
        bot.send_message(call.message.chat.id, "📁 Выберите категорию", reply_markup=keyboard)

    # удаление категории
    elif call_data[0] == "!del_cat":
        keyboard = telebot.types.InlineKeyboardMarkup()

        keyboard.add(
            telebot.types.InlineKeyboardButton(text=YES, callback_data=f"del_cat={call_data[1]}"))
        keyboard.add(
            telebot.types.InlineKeyboardButton(text=NO, callback_data="cancel"))

        bot.send_message(call.message.chat.id, f"❓ Удалить категорию *{database.get_category(call_data[1])}*❓ \n"
                                               "*Будут удалены ВСЕ ТОВАРЫ в данной категории*", reply_markup=keyboard)
    elif call_data[0] == "del_cat":
        database.delete_category(call_data[1])
        bot.send_message(call.message.chat.id, f"❗ Категория удалена ❗")

    # Удаление подкатегории
    elif call_data[0] == "!del_subcat":
        cat = call_data[1].split("|")

        keyboard = telebot.types.InlineKeyboardMarkup()
        subcategory_list = database.get_subcategory(cat[0])
        keyboard.add(
            telebot.types.InlineKeyboardButton(text=YES, callback_data=f"del_subcat={call_data[1]}"))
        keyboard.add(
            telebot.types.InlineKeyboardButton(text=NO, callback_data="cancel"))

        bot.send_message(call.message.chat.id, f"❓ Удалить категорию *{subcategory_list}*❓ \n"
                                               "*Будут удалены ВСЕ ТОВАРЫ в данной категории*", reply_markup=keyboard)
    elif call_data[0] == "del_subcat":
        cat = call_data[1].split("|")
        database.delete_subcategory(cat[0], cat[1])
        bot.send_message(call.message.chat.id, f"❗ Подкатегория удалена")

    # страница со всеми запросами
    elif call_data[0] == "get_support":
        temp_data = call_data[1].split("|")

        keyboard = support.get_support_msg(temp_data[1])
        bot.send_message(call.message.chat.id, "👨‍💻 История запросов", reply_markup=keyboard)

    elif call_data[0] == "select_support":
        msg, keyboard = support.get_sup_msg(call_data[1])
        bot.send_message(call.message.chat.id, msg, reply_markup=keyboard)

    # Ответ на обращение
    elif call_data[0] == "ans_sup":
        bot.send_message(call.message.chat.id, "✏ Напишите ответ")
        bot.register_next_step_handler(call.message, send_support_answer, call_data[1].split("|")[0])

    # Удалить обращение
    elif call_data[0] == "del_sup":
        database.delete_support(call_data[1])

    # редактировать сообщение поддержки
    elif call_data[0] == "edit_supmes":
        bot.send_message(call.message.chat.id, "📝 Введите сообщение")
        bot.register_next_step_handler(call.message, edit_sup_mes)

    # след страница отчета
    elif call_data[0] == "get_report":
        keyboard = stat.get_stat_page(call_data[1])
        bot.send_message(call.message.chat.id, "📆 Выберите дату отчета", reply_markup=keyboard)

    # обработка отчета
    elif call_data[0] == "report":
        msg, keyboard = stat.get_report(call_data[1])
        bot.send_message(call.message.chat.id, msg, reply_markup=keyboard)

    # Кошельки
    elif call_data[0] == "payment":
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton(text="🔄 Проверить доступность",
                                                        callback_data=f"check={call_data[1]}"))
        keyboard.add(telebot.types.InlineKeyboardButton(text="✏ Изменить кошелек",
                                                        callback_data=f"edit={call_data[1]}"))
        if call_data[1] == "qiwi":
            bot.send_message(call.message.chat.id, "🥝 QIWI-Кошелек", reply_markup=keyboard)
        elif call_data[1] == "yoomoney":
            bot.send_message(call.message.chat.id, "💳 YooMoney", reply_markup=keyboard)

    # Проверка кошельков
    elif call_data[0] == "check":
        if call_data[1] == "qiwi":
            if qiwi.check_available():
                bot.send_message(call.message.chat.id, "✅ Кошелек доступен")
            else:
                bot.send_message(call.message.chat.id, "❗ Кошелек не доступен, измените токен ❗")
        elif call_data[1] == "yoomoney":
            if yoomoney.check_yoo():
                bot.send_message(call.message.chat.id, "✅ Кошелек доступен")
            else:
                bot.send_message(call.message.chat.id, "❗ Кошелек не доступен, измените токен ❗")

    # Редактирование кошельков
    elif call_data[0] == "edit":
        if call_data[1] == "qiwi":
            bot.send_message(call.message.chat.id, "✏ Введите номер кошелька")
            bot.register_next_step_handler(call.message, qiwi_payment)
        elif call_data[1] == "yoomoney":
            bot.send_message(call.message.chat.id, "✏ Введите client id")
            bot.register_next_step_handler(call.message, yoo_client)

@bot.callback_query_handler(func=lambda call: True)
def cancel_handler(call):
    if call.data == "cancel":
        bot.delete_message(call.message.chat.id, call.message.message_id)
    else:
        bot.send_message(call.message.chat.id, "! Bad Request !")


# инфа о товаре
def get_item_msg(message, id):
    global item_editor
    item_editor = item_menu.ItemEditor(id)
    bot.send_message(message.chat.id, item_editor.get_text(), reply_markup=item_editor.get_keyboard(),
                     parse_mode="HTML")


def get_item_data(message, id):
    msg, keyboard = item_editor.select_data(id)
    bot.send_message(message.chat.id, msg, reply_markup=keyboard, parse_mode="HTML")


# FAQ
def edit_faq(message):
    if not_const(message.text):
        database.input_faq(message.text)
        bot.send_message(message.from_user.id, "ℹ FAQ успешно обновлен")
    else:
        bot.send_message(message.from_user.id, "❗ Неправильный формат данных ❗")
        return


# Рассылка
@async_dec()
def create_sending(message):
    user_list = database.get_user_list()
    all_send_mes = 0
    limit = 0

    if message.photo is not None or message.document is not None:
        sending_text = message.caption
        folder = "sendings"
        if os.path.exists(folder) is False:
            os.mkdir(folder)

        if message.photo is not None:
            file_info = bot.get_file(message.photo[-1].file_id)
            name = message.photo[1].file_unique_id
        else:
            file_info = bot.get_file(message.document.file_id)
            name = message.document.file_unique_id

        file_info = file_info.wait()
        downloaded_file = bot.download_file(file_info.file_path)
        downloaded_file = downloaded_file.wait()

        src = f"{folder}/{name}"
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)

        if not_const(sending_text):
            for i in range(len(user_list)):
                try:
                    if limit <= 20:
                        bot.send_photo(user_list[i][0],
                                       photo=open(src, "rb"),
                                       caption=sending_text,
                                       parse_mode="HTML")
                        limit += 1
                        all_send_mes += 1
                    else:
                        limit = 0
                        time.sleep(2)
                except:
                    continue
        else:
            bot.send_message(message.from_user.id, "❗ Неправильный формат данных ❗")
            return
    else:
        sending_text = message.text

        if not_const(sending_text):
            for i in range(len(user_list)):
                try:
                    if limit <= 20:
                        bot.send_message(user_list[i][0], sending_text, parse_mode="HTML")
                        limit += 1
                        all_send_mes += 1
                    else:
                        limit = 0
                        time.sleep(2)
                except:
                    continue
        else:
            bot.send_message(message.from_user.id, "❗ Неправильный формат данных ❗")
            return

    bot.send_message(message.from_user.id, string_help.get_text_send(all_send_mes))


# Текст обращения в поддержку
def send_support(message, support_theme):
    if not_const(message.text):
        if message.text is not None:
            id_user = message.chat.id
            support_mess = message.text

            database.send_appeal(id_user, support_mess, support_theme)

            msg = "📢🐘 <b>Лошара написал!</b>\n" \
                  f"🔹 ID лоха: <b>{message.from_user.username}</b>\n" \
                  f"🔹 Тип обращения: {support_theme}\n" \
                  f"🔹 Сообщение: {support_mess}"

            send_admin_mes(msg)

            bot.send_message(message.from_user.id,
                             "✅ Ваше обращение было доставлено\n⏲Ждите ответа в ближайшее время")
        else:
            bot.send_message(message.from_user.id, "❗ Обращение не может быть пустым ❗")
            return
    else:
        bot.send_message(message.from_user.id, "❗ Обращение не может содержать в себе названия кнопок ❗")
        return


# Ответ на обращение
def send_support_answer(message, id_chat):
    if not_const(message.text):
        answer = str(message.text)
        user_id = database.send_appeal_answer(id_chat, answer)
        mes = f"✅ Ваше обращение было рассмотрено: \n\n" + answer

        bot.send_message(user_id, mes)
        send_admin_mes(f"{message.chat.username} ответил на запрос от {user_id} \n{answer}")
    else:
        bot.send_message(message.from_user.id, "❗ Неправильный формат данных ❗")
        return


# сообщение поддержки
def edit_sup_mes(message):
    msg = str(message.text)

    if not_const(msg):
        database.input_sup_mes(msg)
        bot.send_message(message.from_user.id, "✅ Сообщение обновлено")
    else:
        bot.send_message(message.from_user.id, "❗ Неправильный формат данных ❗")
        return


# Кошельки
# QIWI
def qiwi_payment(message):
    if not_const(message.text):
        bot.send_message(message.from_user.id, "✏ Введите токен QIWI")
        bot.register_next_step_handler(message, qiwi_token_payment, message.text)
    else:
        bot.send_message(message.from_user.id, "❗ Неправильный формат данных ❗")
        return


# токен
def qiwi_token_payment(message, qiwi_number):
    try:
        bot.delete_message(message.chat.id, message.message_id)
        qiwi_update = qiwi.check_available_data(message.text, qiwi_number)
        if qiwi_update:
            database.input_qiwi(message.text, qiwi_number)
            qiwi.update()
            bot.send_message(message.from_user.id, "🔐 Токен был успешно изменен!")
        else:
            bot.send_message(message.from_user.id, "❗ Неверный токен ❗")

    except:
        bot.delete_message(message.chat.id, message.message_id)
        bot.send_message(message.from_user.id, "❗ Ошибка токена ❗")


# YooMoney
# client_id
def yoo_client(message):
    if not_const(message.text):
        global client_id
        client_id = message.text
        bot.send_message(message.from_user.id,
                         "✏ Введите ссылку на переадресацию, которую вы указали при регистрации приложения")
        bot.register_next_step_handler(message, yoo_redirect)
    else:
        bot.send_message(message.from_user.id, "❗ Неправильный формат данных ❗")
        return


# Переадресация
def yoo_redirect(message):
    if not_const(message.text):
        global redirect
        redirect = message.text

        link = yoomoney.gen_auth(client_id, redirect)
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton(
            text="💻 Активация", url=link
        ))
        bot.send_message(message.chat.id, "❗ Перейдите по ссылке, подтвердите данные и скопируйте полученную ссылку "
                                          "после переадресации.\n"
                                          "❗ Время действия полученной ссылки *1 минута*", reply_markup=keyboard)
        bot.register_next_step_handler(message, yoo_url)
    else:
        bot.send_message(message.from_user.id, "❗ Неправильный формат данных ❗")
        return


# Полученная ссылка
def yoo_url(message):
    if not_const(message.text):
        result = yoomoney.gen_token(message.text)
        if result:
            bot.send_message(message.from_user.id, "🔐 Токен был успешно изменен!")
        else:
            bot.send_message(message.from_user.id, "❗ Ошибка в выполнении ❗")
    else:
        bot.send_message(message.from_user.id, "❗ Неправильный формат данных ❗")
        return


# Добавление категории / подкатегории
# Категория
def new_category(message):
    category_creator.category = str(message.text)
    bot.send_message(message.from_user.id,
                     string_help.get_text_cat(category_creator.create_category()))


# Подкатегория
def new_subcategory(message):
    category_creator.subcategory = str(message.text)
    bot.send_message(message.from_user.id,
                     string_help.get_text_cat(category_creator.create_subcategory()))


# проверка количества товара
def check_count(message, item_id, limit):
    try:
        user_count = int(message.text)

        if int(limit) >= user_count > 0:
            select_pay(message, f"{item_id}|{user_count}")
        else:
            bot.send_message(message.from_user.id, "❗ Некорректное количество товара")
    except Exception:
        bot.send_message(message.from_user.id, "❗ Неправильный формат данных ❗")
        return


# выбор оплаты
def select_pay(message, data):
    keyboard = telebot.types.InlineKeyboardMarkup()
    available = False

    if qiwi.check_available():
        keyboard.add(telebot.types.InlineKeyboardButton(
            text="🥝 QIWI", callback_data=f"buy_item={data}|qiwi"))
        available = True

    if yoomoney.check_yoo():
        keyboard.add(telebot.types.InlineKeyboardButton(
            text="💳 YooMoney", callback_data=f"buy_item={data}|yoo"))
        available = True

    keyboard.add(telebot.types.InlineKeyboardButton(text=CLOSE, callback_data=f"cancel"))
    if available:
        msg = "💰 Выберите способ оплаты"
    else:
        msg = "😔 Извините, но оплата на данный момент не работает \n Приносим свои извинения"

    bot.send_message(message.chat.id, msg, reply_markup=keyboard)


# покупка товара
def buy_item(message, data):
    booking.create_booking(message.chat.id)

    temp_data = data.split("|")

    item_id = temp_data[0]
    count_buy = int(temp_data[1])
    pay_method = temp_data[2]

    if not qiwi.check_available():
        bot.send_message(message.chat.id,
                         "😔 Извините, но оплата на данный момент не работает \n Приносим свои извинения")
        send_admin_mes("❗ Не работает оплата через <b>QIWI</b> ❗")
        return

    item = database.get_item_by_id(item_id)

    item_name = item[1]
    item_price = int(item[3]) * count_buy
    count = item[6]

    if pay_method == "qiwi":
        num = qiwi.num
        comment, pay_link = qiwi.create_link(item_price)
    elif pay_method == "yoo":
        num = yoomoney.num
        comment, pay_link = yoomoney.create_link(item_price)

    if count > 0:
        booking.add_booking(message.chat.id, item_name, database.get_items_id(item_name, count_buy))

        message_pay = string_help.get_buy_message(item_name, num, comment, item_price)

        selected_item = f"selected_item={item_id}"

        if item_id is None:
            item_id = database.get_item(data[1])[0]

        check = f"check_pay={pay_method}|{comment}|{item_id}|{count_buy}"

        keyboard = keyboards.create_check_buttons(pay_link, check, selected_item)
        bot.send_message(message.chat.id, message_pay, reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "😔 Извините, но данного товара сейчас нет в наличии")


# Добавление товара
# Название
def add_item_name(message):
    name = message.text
    if not_const(name):
        item_creator.name = name
        bot.send_message(message.from_user.id, "✏ Введите описание товара")
        bot.register_next_step_handler(message, add_item_desc)
    else:
        bot.reply_to(message, "❗ Неправильный формат данных ❗\n📚 Введите название товара")
        bot.register_next_step_handler(message, add_item_name)


# Описание
def add_item_desc(message):
    desc = message.text
    if not_const(desc):
        item_creator.desc = desc
        bot.send_message(message.from_user.id, "💵 Введите стоимость товара (в рублях)")
        bot.register_next_step_handler(message, add_item_price)
    else:
        bot.reply_to(message, "❗ Неправильный формат данных ❗\n✏ Введите описание товара")
        bot.register_next_step_handler(message, add_item_desc)


# Цена
def add_item_price(message):
    try:
        price = int(message.text)
        if not_const(price):
            item_creator.price = price
            bot.send_message(message.from_user.id, "🔐 Введите данные товара \n*Один товар - Одна строка* \n"
                                                   "💾 Или же загрузите архив или файл с товаром")
            bot.register_next_step_handler(message, add_item_data)
        else:
            bot.reply_to(message, "❗ Неправильный формат данных ❗\n💵 Введите стоимость товара (в рублях)")
            bot.register_next_step_handler(message, add_item_price)
    except Exception:
        bot.reply_to(message, "❗ Неправильный формат данных ❗\n💵 Введите стоимость товара (в рублях)")
        bot.register_next_step_handler(message, add_item_price)


# Данные товаров
def add_item_data(message: telebot.types.Message):
    if message.document is not None:
        # архив
        try:
            file_info = bot.get_file(message.document.file_id)
            file_info = file_info.wait()
            downloaded_file = bot.download_file(file_info.file_path)
            downloaded_file = downloaded_file.wait()

            folder = f"items"
            if not os.path.exists(folder):
                os.mkdir(folder)

            src = f"{folder}/{message.document.file_name}"
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)

            item_creator.data = f"[file]={src}"
        except Exception:
            bot.send_message(message.from_user.id, "❗ Ошибка при загрузке ❗")
            return

        item_creator.input_file()
        bot.send_message(message.chat.id, "📦 Товар добавлен")
    else:
        # текст
        item_creator.data = str(message.text).split("\n")
        item_creator.input_item()
        count = len(item_creator.data)

        bot.send_message(message.from_user.id, string_help.get_text_itmes(count))


# # # # # # # #
# Редактирование товаров
# Название
def edit_name(message):
    new_name = message.text
    if not_const(new_name):
        item_editor.update_name(new_name)
        bot.send_message(message.from_user.id, "📝 Имя изменено")
        get_item_msg(message, item_editor.id)
    else:
        bot.send_message(message.from_user.id, "❗ Неправильный формат данных ❗")
        get_item_msg(message, item_editor.id)


# Описание
def edit_desc(message):
    new_desc = message.text
    if not_const(new_desc):
        item_editor.update_desc(new_desc)
        bot.send_message(message.from_user.id, "📝 Описание изменено")
        get_item_msg(message, item_editor.id)
    else:
        bot.send_message(message.from_user.id, "❗ Неправильный формат данных ❗")
        get_item_msg(message, item_editor.id)


# Цена
def edit_price(message):
    if not_const(message.text):
        try:
            new_price = int(message.text)
            item_editor.update_price(new_price)
            bot.send_message(message.from_user.id, "📝 Цена изменена")
            get_item_msg(message, item_editor.id)
        except ValueError:
            bot.send_message(message.chat.id, "📝 Введите цену")
            bot.register_next_step_handler(message, edit_price)
    else:
        bot.send_message(message.from_user.id, "❗ Неправильный формат данных ❗")
        get_item_msg(message, item_editor.id)


# Данные
def edit_data(message):
    if not_const(message.text):
        item_editor.update_data(message.text)
        bot.send_message(message.from_user.id, "📝 Данные изменены")
        get_item_data(message, item_editor.id_edit)
    else:
        bot.send_message(message.from_user.id, "❗ Неправильный формат данных ❗")
        get_item_msg(message, item_editor.id)


# Добавление данных
@bot.message_handler(content_types=['document'])
def add_data(message):
    if item_editor.name == "":
        return

    if message.document is not None:
        # архив
        try:
            file_info = bot.get_file(message.document.file_id)
            file_info = file_info.wait()
            downloaded_file = bot.download_file(file_info.file_path)
            downloaded_file = downloaded_file.wait()

            folder = f"items"
            if not os.path.exists(folder):
                os.mkdir(folder)

            src = f"{folder}/{message.document.file_name}"
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)

            file_data = f"[file]={src}"
        except Exception as e:
            bot.send_message(message.from_user.id, f"❗ Ошибка при загрузке ❗")
            return

        item_editor.add_file(file_data)
        bot.send_message(message.chat.id, "📦 Товар добавлен")
    else:
        # текст
        data = str(message.text)
        data_list = data.split("\n")

        count = len(data_list)
        item_editor.add_data(data_list)
        bot.send_message(message.from_user.id, string_help.get_text_itmes(count))
        get_item_msg(message, item_editor.id)


       



# Запуск бота
if __name__ == '__main__':
    while True:
        try:
            print("Бот запущен!")
            bot.polling(none_stop=True)
        except Exception as e:
            send_admin_mes(f"❗ Ошибка при работе бота ❗\n<b>{e}</b>\n❗ Необходим перезапуск бота ❗")
            sys.exit()
