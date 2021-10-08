from datetime import datetime

import telebot

import gonal_database as database
from src import gonal_const as const
from src import gonal_keyboards as keyboards


def get_ten_data(names, params: dict):
    count = 0
    data = ""
    while count < 10 and count < len(params):
        data += f"▫ {names[count]} – {params.get(names[count])}\n"
        count += 1

    return data


class Stat:
    def __init__(self):
        self.date_sort = []
        self.fabric = None
        self.last_page = 0

    def create_fabric(self):
        self.fabric = keyboards.PageKeyboardFabric(self.date_sort,
                                                   "stat_date",
                                                   "report",
                                                   "get_report=",
                                                   "cancel")

    def get_all_stat(self):
        user_count = len(database.get_user_list())
        sales_list = database.get_sales()
        sales_len = len(sales_list)

        sales_sum = 0
        sales_most = dict()
        buyers_most = dict()
        for i in range(sales_len):
            sales_sum += int(sales_list[i][4])

            buyer = sales_list[i][0]
            name = sales_list[i][1]
            if name in sales_most:
                sales_most.update({name: int(sales_most.get(name)) + 1})
            else:
                sales_most[name] = int(1)

            if buyer in buyers_most:
                buyers_most.update({buyer: int(buyers_most.get(buyer) + 1)})
            else:
                buyers_most[buyer] = int(1)

        sales_sort = sorted(sales_most, key=sales_most.get, reverse=True)
        buyers_sort = sorted(buyers_most, key=buyers_most.get, reverse=True)

        sales_list = {}
        buyers_list = {}
        for i in sales_sort:
            sales_list[i] = sales_most[i]
        for i in buyers_sort:
            buyers_list[i] = buyers_most[i]

        sales = get_ten_data(sales_sort, sales_most)
        buyers = get_ten_data(buyers_sort, buyers_most)

        msg = "📊 Статистика магазина\n\n" \
              f"💻 Количество пользователей: {user_count}\n" \
              f"💰 Прибыль магазина: {sales_sum} руб.\n\n" \
              f"🛒 Часто покупаемые товары: \n{sales}\n" \
              f"💳 Активные покупатели: \n{buyers}"

        return msg

    def create_date_list(self):
        sales_list = database.get_sales_data()
        date_list = []
        for i in range(len(sales_list)):
            date = sales_list[i][0]
            if date not in date_list:
                date_list.append(date)
        dates = []
        for i in date_list:
            date = datetime.strptime(i, "%d/%m/%Y")
            if date not in dates:
                dates.append(date)
        dates.sort()

        self.date_sort = []
        for date in dates:
            date_str = f"{date.day}/{date.month}/{date.year}"
            self.date_sort.append(date_str)
        self.date_sort.reverse()
        self.create_fabric()

    def get_stat_page(self, page):
        self.last_page = page
        return self.fabric.create_keyboard(page)

    def get_report(self, temp):
        temp = temp.split("|")
        date = temp[0]

        data = database.get_sales_info_day(date)
        msg = f"📆 Отчет за {date}\n\n"

        buyer_list = []
        sum = 0
        for i in range(len(data)):
            buyer = data[i][0]
            if buyer not in buyer_list:
                msg += f"➖ {buyer}\n"
                for j in range(len(data)):
                    if data[j][0] == buyer:
                        msg += f"  ▪ {data[j][1]} : {data[j][4]} руб.\n"
                        sum += int(data[j][4])
                buyer_list.append(buyer)
            else:
                continue

        msg += f"\n💰 Прибыль: {sum} руб."

        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton(text=const.BACK,
                                                        callback_data=f"get_report={self.last_page}"))
        keyboard.add(telebot.types.InlineKeyboardButton(text=const.CLOSE,
                                                        callback_data="cancel"))

        return msg, keyboard


def get_stat(message):
    sales_list = database.get_user_sales(message.chat.id)

    msg = f"💻 Пользователь: @{message.from_user.username}\n" \
          f"🛒 Количество покупок: {len(sales_list)}"

    return msg
