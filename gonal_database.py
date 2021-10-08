import sqlite3

import gonal_strings as str_help
from src import gonal_booking as booking

DATABASE = "shop.sqlite"

def connect_db():
    return sqlite3.connect(DATABASE)

def open_db():
    with connect_db() as db:
        cur = db.cursor()

        try:
            cur.execute("SELECT * FROM Items")
            print("БД 'Товары' работает")
        except sqlite3.OperationalError:
            cur.execute("CREATE TABLE Items("
                        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                        "name TEXT, "
                        "desc TEXT, "
                        "price INT, "
                        "category TEXT, "
                        "subCategory TEXT, "
                        "data TEXT)")
            print("БД 'Товары' создана")

        try:
            cur.execute("SELECT * FROM ItemsCount")
            print("БД 'Товары Кол-во' работает")
        except sqlite3.OperationalError:
            cur.execute("CREATE TABLE ItemsCount("
                        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                        "name TEXT, "
                        "desc TEXT, "
                        "price INT, "
                        "category TEXT, "
                        "subCategory TEXT, "
                        "count INT)")
            print("БД 'Товары Кол-во' создана")

        try:
            cur.execute("SELECT * FROM Category")
            print("БД 'Категории' работает")
        except sqlite3.OperationalError:
            cur.execute("CREATE TABLE Category("
                        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                        "category TEXT)")
            print("БД 'Категории' создана")

        try:
            cur.execute("SELECT * FROM SubCategory")
            print("БД 'Подкатегории' работает")
        except sqlite3.OperationalError:
            cur.execute("CREATE TABLE SubCategory("
                        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                        "name_subcat TEXT, "
                        "main_category TEXT)")
            print("БД 'Подкатегории' создана")

        try:
            cur.execute("SELECT * FROM Faq")
            print("БД 'FAQ' работает")
        except sqlite3.OperationalError:
            cur.execute("CREATE TABLE Faq("
                        "help TEXT)")
            row = cur.fetchone()
            if row is None:
                cur.execute("DROP TABLE Faq")
                cur.execute("CREATE TABLE Faq("
                            "help TEXT)")
                cur.execute("INSERT INTO Faq VALUES(?)",
                            ["✒Пример FAQ для вашего магазина\nВы можете изменить его в главном меню "
                             "\n<b>Разработано GonalInc</b>"])
                print("БД 'FAQ' созданна")
            else:
                print("БД 'FAQ' созданна")

        try:
            cur.execute("SELECT * FROM Qiwi")
            print("БД 'Qiwi' работает")
        except sqlite3.OperationalError:
            cur.execute("CREATE TABLE Qiwi("
                        "number TEXT, "
                        "token TEXT)")
            row = cur.fetchone()
            if row is None:
                cur.executemany("INSERT INTO Qiwi(number, token) "
                                "VALUES (?, ?)", [("number", "token")])
                print("БД 'Qiwi' создана")
            else:
                print("БД 'Qiwi' создана")

        try:
            cur.execute("SELECT * FROM YooMoney")
            print("БД 'YooMoney' работает")
        except sqlite3.OperationalError:
            cur.execute("CREATE TABLE YooMoney("
                        "number TEXT, "
                        "token TEXT)")
            row = cur.fetchone()
            if row is None:
                cur.executemany("INSERT INTO YooMoney(number, token) "
                                "VALUES (?, ?)", [("number", "token")])
                print("БД 'YooMoney' создана")
            else:
                print("БД 'YooMoney' создана")

        try:
            cur.execute("SELECT * FROM Sales")
            print("БД 'Продажи' работает")
        except sqlite3.OperationalError:
            cur.execute("CREATE TABLE Sales("
                        "user TEXT,"
                        "item TEXT, "
                        "item_ID TEXT,"
                        "comment TEXT, "
                        "price TEXT, "
                        "data TEXT,"
                        "time TEXT)")
            print("БД 'Продажи' создана")

        try:
            cur.execute("SELECT * FROM SupportMes")
            print("БД 'Обращения' работает")
        except sqlite3.OperationalError:
            cur.execute("CREATE TABLE SupportMes("
                        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                        "chatID TEXT, "
                        "message TEXT, "
                        "type TEXT, "
                        "state TEXT,"
                        "time TEXT,"
                        "answer TEXT)")
            print("БД 'Обращения' создана")

        try:
            cur.execute("SELECT * FROM SupportAdmin")
            print("БД 'Сообщение Поддержки' работает")
        except sqlite3.OperationalError:
            cur.execute("CREATE TABLE SupportAdmin("
                        "message TEXT)")
            cur.execute("INSERT INTO SupportAdmin VALUES (?)",
                        ["✒ Пример сообщения поддержки, которое показывается пользователям\nЕго можно изменить в меню"]
                        )
            print("БД 'Сообщение Поддержки' создана")

        try:
            cur.execute("SELECT * FROM UserList")
            print("БД 'Пользователи' работает")
        except sqlite3.OperationalError:
            cur.execute("CREATE TABLE UserList(chatID TEXT)")
            print("БД 'Пользователи' создана")


def get_user_list():
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM UserList")

    return cur.fetchall()


def get_categories():
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM Category")

    return cur.fetchall()


def get_category(id):
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM Category WHERE id = ?", [id])

    return cur.fetchall()[0][1]


def get_subcategory(id):
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM SubCategory WHERE id = ?", [id])

    return cur.fetchall()[0][1]


def get_category_name(category):
    with connect_db() as db:
        cur = db.cursor()
        data = cur.execute("SELECT * FROM Category WHERE category = ?", [category]).fetchall()
        if len(data) > 0:
            return True
        else:
            return False


def get_subcat_name(name):
    with connect_db() as db:
        cur = db.cursor()
        data = cur.execute("SELECT * FROM SubCategory WHERE name_subcat = ?", [name]).fetchall()
        if len(data) > 0:
            return True
        else:
            return False


def get_faq():
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM Faq")

    return cur.fetchall()


def get_support_mes(state):
    if state:
        s = "✅ Отвечено"
    else:
        s = "❌ Не отвечено"

    with connect_db() as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM SupportMes WHERE state = ?", [s])

    return cur.fetchall()


def get_support_mes_id(id):
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM SupportMes WHERE id = ?", [id])

    return cur.fetchone()


def get_support_main_mes():
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM SupportAdmin")

    return cur.fetchone()


def get_subcategories(category):
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM SubCategory WHERE main_category = ?", [category])

    return cur.fetchall()


def get_all_items():
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM ItemsCount")

    return cur.fetchall()


def get_items(category, sub_cat):
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM ItemsCount WHERE category = ? AND subCategory = ?", (category, sub_cat))

    return cur.fetchall()


def get_item(name):
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM ItemsCount WHERE name = ?", [name])

    return cur.fetchone()


def get_item_by_id(id):
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM ItemsCount WHERE id = ?", [id])

    return cur.fetchone()


def get_item_id(name):
    id = -1

    with connect_db() as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM Items WHERE name = ?", [name])
        while True:
            row = cur.fetchone()
            if row is None:
                break
            else:
                id = row[0]
                break
    return id


def get_items_id(name, count):
    id_list = []

    with connect_db() as db:
        cur = db.cursor()
        item_list = cur.execute("SELECT * FROM Items WHERE name = ?", [name]).fetchall()

        for i in range(len(item_list)):
            item_id = item_list[i][0]

            if booking.is_booking(item_id) is False:
                id_list.append(item_id)

            if len(id_list) == count:
                break

    return id_list


def get_all_item(name):
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM Items WHERE name = ?", [name])
        return cur.fetchall()


def get_item_from_id(id):
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM Items WHERE id = ?", [id])
    return cur.fetchone()


def get_sales():
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM Sales")

    return cur.fetchall()


def get_sale_id(user, item_id):
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM Sales WHERE user = ? AND item_ID = ?",
                    (user, item_id))
        return cur.fetchall()


def get_sales_data():
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("SELECT time FROM Sales")

    return cur.fetchall()


def get_sales_info_day(date):
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM Sales WHERE time = ?", [date])

    return cur.fetchall()


def get_user_sales(user_id):
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM Sales WHERE user = ?", [user_id])

    return cur.fetchall()


def get_item_data(id):
    with connect_db() as db:
        cur = db.cursor()
        item_list = cur.execute("SELECT * FROM Items WHERE id = ?", [id]).fetchall()

    return str(item_list[0][6])


def get_qiwi(key):
    with connect_db() as db:
        cur = db.cursor()
        data = cur.execute("SELECT * FROM Qiwi").fetchall()[0][key]

    return data


def get_yoo(key):
    # 0 - номер
    # 1 - токен
    with connect_db() as db:
        cur = db.cursor()
        data = cur.execute("SELECT * FROM YooMoney").fetchall()[0][key]

    return data


def input_category(name):
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("INSERT INTO Category (category) VALUES (?)", [name])


def input_subcategory(name, main_category):
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("INSERT INTO SubCategory (name_subcat, main_category) VALUES (?, ?)",
                    (name, main_category))


def input_item_file(name, desc, price, subcategory, category, file_path):
    with connect_db() as db:
        cur = db.cursor()

        cur.execute(
            "INSERT INTO Items (name, desc, price, subCategory, category, data) VALUES (?, ?, ?, ?, ?, ?)",
            (name, desc, price, subcategory, category, file_path))

        if not is_available_item(name):
            cur.execute(
                "INSERT INTO ItemsCount (name, desc, price, subCategory, category, count) VALUES (?, ?, ?, ?, ?, ?)",
                (name, desc, price, subcategory, category, 1))
        else:
            data = get_item(name)

            new_count = int(data[6]) + 1
            if len(data) > 0:
                cur.execute("UPDATE ItemsCount SET count = ? WHERE name = ?", (new_count, name))

def input_item(name, desc, price, subcategory, category, data_list):
    count = len(data_list)
    with connect_db() as db:
        cur = db.cursor()
        if not is_available_item(name):
            cur.execute(
                "INSERT INTO ItemsCount (name, desc, price, subCategory, category, count) VALUES (?, ?, ?, ?, ?, ?)",
                (name, desc, price, subcategory, category, count))

            for i in range(count):
                cur.execute(
                    "INSERT INTO Items (name, desc, price, subCategory, category, data) VALUES (?, ?, ?, ?, ?, ?)",
                    (name, desc, price, subcategory, category, data_list[i]))
        else:
            data = get_item(name)

            item_desc = data[2]
            item_price = data[3]
            item_cat = data[4]
            item_subcat = data[5]
            item_count = data[6]

            new_count = count + item_count

            for i in range(count):
                cur.execute(
                    "INSERT INTO Items (name, desc, price, subCategory, category, data) VALUES (?, ?, ?, ?, ?, ?)",
                    (name, item_desc, item_price, item_subcat, item_cat, data_list[i]))

            cur.execute("UPDATE ItemsCount SET count = ? WHERE name = ?", (new_count, name))


def is_available_item(name):
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM ItemsCount WHERE name = ?", (name,))

        is_available = False
        while True:
            row = cur.fetchone()
            if row is None:
                break
            if row[6] >= 0:
                is_available = True
                break

    return is_available


def input_info_buy(user_id, item_name, item_id, comment, item_price, item_data, time):
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("INSERT INTO Sales(user, item, item_ID, comment, price, data, time) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (user_id, item_name, item_id, comment, item_price, item_data, time))

        cur.execute("DELETE FROM Items WHERE id = ?", [item_id])
        list_item = get_item(item_name)
        count = list_item[6]
        count = count - 1
        cur.execute("UPDATE ItemsCount SET count = ? WHERE name = ?", (count, item_name))


def input_user(id):
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM UserList WHERE chatID = ?", [id])
        row = cur.fetchall()
        if len(row) == 0:
            cur.execute("INSERT INTO UserList (chatID) VALUES (?)", [id])
            return True
        else:
            return False


def input_sup_mes(msg):
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM SupportAdmin")
        row = cur.fetchone()

        cur.execute("UPDATE SupportAdmin SET message = ? WHERE message = ?", (msg, row[0]))


def input_faq(text):
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM Faq")
        while True:
            row = cur.fetchone()
            if row is None:
                break
            cur.execute("UPDATE Faq SET help = ? WHERE help = ?", (text, row[0]))


def input_qiwi(token, number):
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM Qiwi")
        while True:
            row = cur.fetchone()
            if row is None:
                break
            old_num = row[0]
            cur.execute("UPDATE Qiwi SET number = ?, token = ? WHERE number = ?",
                        (number, token, old_num))


# добавить yoo money
def input_yoo_money(number, token):
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM YooMoney")
        while True:
            row = cur.fetchone()
            if row is None:
                break
            old_num = row[0]
            cur.execute("UPDATE YooMoney SET number = ?, token = ? WHERE number = ?",
                        (number, token, old_num))


def send_appeal(id_user, message, theme):
    with connect_db() as db:
        cur = db.cursor()

        now_date = str_help.get_time_format()
        cur.execute("INSERT INTO SupportMes (chatID, message, type, state, time, answer) VALUES (?, ?, ?, ?, ?, ?)",
                    (id_user, message, theme, "❌ Не отвечено", now_date, ""))


def send_appeal_answer(id_chat, answer):
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM SupportMes WHERE id = ?", (id_chat,))
        row = cur.fetchone()

        cur.execute("UPDATE SupportMes SET state = ? WHERE id = ?", ("✅ Отвечено", id_chat))
        cur.execute("UPDATE SupportMes SET answer = ? WHERE id = ?", (answer, id_chat))

    return row[1]


def delete_item(id):
    with connect_db() as db:
        cur = db.cursor()
        name = cur.execute("SELECT * FROM ItemsCount WHERE id = ?", [id]).fetchone()[1]

        cur.execute("DELETE FROM Items WHERE name = ?", [name])
        cur.execute("DELETE FROM ItemsCount WHERE name = ?", [name])


def delete_category(category):
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("DELETE FROM Category WHERE id = ?", [category])
        cur.execute("DELETE FROM SubCategory WHERE main_category = ?", [category])
        cur.execute("DELETE FROM Items WHERE category = ?", [category])
        cur.execute("DELETE FROM ItemsCount WHERE category = ?", [category])


def delete_subcategory(main_cat, sub_cat):
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("DELETE FROM SubCategory WHERE id = ? AND main_category = ?", (main_cat, sub_cat))
        cur.execute("DELETE FROM ItemsCount WHERE subCategory = ? AND category = ?", (main_cat, sub_cat))
        cur.execute("DELETE FROM Items WHERE subCategory = ? AND category = ?", (main_cat, sub_cat))


def delete_support(id):
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("DELETE FROM SupportMes WHERE id = ?", [id])


def edit_item_name(id, new_name):
    old_name = get_item_by_id(id)[1]

    with connect_db() as db:
        cur = db.cursor()
        cur.execute("UPDATE ItemsCount SET name = ? WHERE name = ?", (new_name, old_name))
        cur.execute("UPDATE Items SET name = ? WHERE name = ?", (new_name, old_name))


def edit_item_desc(id, new_desc):
    name = get_item_by_id(id)[1]

    with connect_db() as db:
        cur = db.cursor()
        cur.execute("UPDATE ItemsCount SET desc = ? WHERE name = ?", (new_desc, name))
        cur.execute("UPDATE Items SET desc = ? WHERE name = ?", (new_desc, name))


def edit_item_price(id, new_price):
    name = get_item_by_id(id)[1]

    with connect_db() as db:
        cur = db.cursor()
        cur.execute("UPDATE ItemsCount SET price = ? WHERE name = ?", (new_price, name))
        cur.execute("UPDATE Items SET price = ? WHERE name = ?", (new_price, name))


def edit_item_data(id, new_data):
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("UPDATE Items SET data = ? WHERE id = ?", (new_data, id))


def delete_item_data(id):
    with connect_db() as db:
        cur = db.cursor()
        item_data = cur.execute("SELECT * FROM Items WHERE id = ?", [id]).fetchone()
        count = cur.execute("SELECT * FROM ItemsCount WHERE name = ?", [item_data[1]]).fetchone()[6]
        count = count - 1

        cur.execute("DELETE FROM Items WHERE id = ?", [id])
        cur.execute("UPDATE ItemsCount SET count = ? WHERE name = ?", (count, item_data[1]))
