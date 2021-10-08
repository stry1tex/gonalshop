DATABASE = "shop.sqlite"
BUY = "💵 Купить"
FAQ = "ℹ FAQ"
REVIEW = "👨‍💻 Поддержка"
PROFILE = "📱 Профиль"

EDIT_FAQ = "✒ Редактировать FAQ"
SUPPORT = "📮 Обращения"
SUPPORT_HISTORY = "📒 История"
SUPPORT_MES = "📋 Описание поддержки"

ADD_ITEM = "📚 Добавить товар"
DELETE_ITEM = "🗑 Удалить товар"
ADD_CATEGORY = "📁 Добавить категорию"
ADD_SUBCATEGORY = "📁 Добавить подкатегорию"
DELETE_CATEGORY = "🚫 Удалить категорию"
DELETE_SUBCATEGORY = "🚫 Удалить подкатегорию"
ITEMS_WORK = "📚 Товары"
EDIT_ITEM = "📝 Управление товарами"
EDIT_NAME = "📙 Изменить название"
EDIT_DESC = "📋 Изменить описание"
EDIT_PRICE = "💵 Изменить цену"
EDIT_DATA = "📦 Редактировать данные"

WORK_PAY = "🔐 Работа с кошельками"
SENDING = "📧 Создать рассылку"
OTHER = "📁 Прочее"
STAT = "📊 Статистика"
REPORT = "📆 Отчеты"
GENERAL = "📋 Общая"

NEXT = "Вперед ➡"
BACK = "⬅ Назад"
RETURN = "◀ Вернуться"
CLOSE = "🚫 Закрыть"
YES = "✔ Да"
NO = "❌ Нет"
DELETE = "🗑 Удалить"

CONST = [
    DATABASE, BUY, EDIT_FAQ, FAQ, REVIEW,
    SUPPORT, SUPPORT_HISTORY, SUPPORT_MES,
    ADD_ITEM, DELETE_ITEM, ADD_CATEGORY, ADD_SUBCATEGORY,
    DELETE_CATEGORY, DELETE_SUBCATEGORY, ITEMS_WORK,
    EDIT_ITEM, EDIT_NAME, EDIT_DESC, EDIT_PRICE, EDIT_DATA,
    WORK_PAY, SENDING, OTHER, STAT, REPORT,
    GENERAL, NEXT, BACK, CLOSE,
    YES, NO, DELETE
]

def not_const(text):
    return not str(text) in CONST
