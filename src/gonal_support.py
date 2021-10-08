from src import gonal_const as const
from src import gonal_keyboards as keyboards
import telebot
import gonal_database as database


class Support:
    def __init__(self):
        self.state = ""
        self.appeals = ""
        self.fabric = None

    # генерация обращений
    def generate_sup_mes(self, state):
        self.state = state
        self.appeals = database.get_support_mes(state)
        self.fabric = keyboards.PageKeyboardFabric(self.appeals,
                                                   "appeals",
                                                   "select_support",
                                                   f"get_support={self.state}|",
                                                   "cancel")

    # сообщения в поддержку
    def get_support_msg(self, page):
        keyboard = self.fabric.create_keyboard(page)

        return keyboard

    # обращение в поддержку
    def get_sup_msg(self, msg_id):
        appeal = database.get_support_mes_id(msg_id)
        keyboard = telebot.types.InlineKeyboardMarkup()

        appeal_id = str(appeal[0])
        appeal_user_id = str(appeal[1])
        appeal_message = str(appeal[2])

        appeal_type = str(appeal[3])
        appeal_answer = str(appeal[6])
        msg = f"🔹 ID Пользователя: {appeal_user_id}\n" \
              f"🔹 Тип обращения: {appeal_type}\n" \
              f"🔹 Сообщение: {appeal_message}\n"

        if self.state:
            msg += f"🔹 Ответ:\n {appeal_answer}"
        else:
            ans_sup = f"ans_sup={appeal_id}|{appeal_user_id}"
            keyboard.add(telebot.types.InlineKeyboardButton(text="✏ Ответить",
                                                            callback_data=ans_sup))

        btn_1 = telebot.types.InlineKeyboardButton(text=const.BACK,
                                                   callback_data=f"get_support={self.state}|0")
        btn_2 = telebot.types.InlineKeyboardButton(text=const.DELETE,
                                                   callback_data=f"del_sup={str(appeal_id)}")
        keyboard.row(btn_1, btn_2)

        return msg, keyboard
