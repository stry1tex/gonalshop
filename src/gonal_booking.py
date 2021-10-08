import threading

booking_list = dict()

thread_dict: dict = {}

# добавить в бронь
def add_booking(user_id, item_name, item_id):
    item_list = {user_id: {item_name: item_id}}
    booking_list.update(item_list)

    t = threading.Timer(300, del_booking, [user_id])
    t.start()

    thread_dict[user_id] = t


# найти бронь на товар
def get_booking(item_name):
    count_booking = 0

    for items in booking_list.values():
        item_list = items.get(item_name)
        if item_list is not None:
            count_booking += len(item_list)

    return count_booking


# проверка на бронирование товара
def is_booking(item_id):
    for basket in booking_list.values():
        if item_id in basket:
            return True

    return False

# удалить бронь
def del_booking(user_id):
    try:
        booking_list.pop(user_id)
        t = thread_dict[user_id]
        t.cancel()

        thread_dict.pop(user_id)
    except Exception as e:
        pass

# очистить/создать бронь
def create_booking(user_id):
    booking_list[user_id] = {}
