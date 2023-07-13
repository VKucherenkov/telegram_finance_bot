""" Работа с расходами — их добавление, удаление, статистики"""
import datetime
import re
from typing import List, NamedTuple, Optional

import pytz

import db
import exceptions
from categories import Categories


class Message(NamedTuple):
    """Структура распаршенного сообщения о новом расходе"""
    amount: float
    category_text: str


class Expense(NamedTuple):
    """Структура добавленного в БД нового расхода"""
    id: Optional[int]
    amount: float
    category_name: str


def add_expense(raw_message: str) -> Expense:
    """Добавляет новое сообщение.
    Принимает на вход текст сообщения, пришедшего в бот."""
    parsed_message = _parse_message(raw_message)
    category = Categories().get_category(
        parsed_message.category_text)
    inserted_row_id = db.insert("expense", {
        "amount": parsed_message.amount,
        "created": _get_now_formatted(),
        "category_codename": category.codename,
        "raw_text": raw_message
    })
    return Expense(id=None,
                   amount=parsed_message.amount,
                   category_name=category.name)


def get_today_statistics() -> str:
    """Возвращает строкой статистику расходов за сегодня"""
    cursor = db.get_cursor()
    cursor.execute(f"SELECT name, SUM(amount), date(created) "
                   f"FROM expense "
                   f"JOIN category ON codename=category_codename "
                   f"GROUP BY name, date(created) "
                   f"HAVING date(created)='{_get_now_formatted()[:10]}'")
    result = cursor.fetchall()
    # print(result)
    if not result:
        return "Сегодня ещё нет расходов"
    all_today_expenses = ''
    all_sum = 0
    for i in result:
        all_today_expenses += f"{i[0]} — {i[1]} руб.\n"
        all_sum += i[1]
    cursor.execute(f"SELECT SUM(amount) "
                   f"FROM expense WHERE date(created)='{_get_now_formatted()[:10]}' "
                   f"AND category_codename IN (SELECT codename "
                   f"FROM category WHERE is_base_expense=TRUE)")
    result = cursor.fetchone()
    base_today_expenses = result[0] if result[0] else 0
    return (f"Расходы сегодня:\n"
            f"Всего — {all_sum} руб., из них:\n"
            f"{all_today_expenses}\n\n"
            f"базовые — {base_today_expenses} руб. из {_get_budget_limit()} руб.\n"
            f"остаток - {_get_budget_limit() - base_today_expenses}\n\n"
            f"За текущий месяц: /month")


def get_month_statistics() -> str:
    """Возвращает строкой статистику расходов за текущий месяц"""
    now = _get_now_datetime()
    first_day_of_month = f'{now.year:04d}-{now.month:02d}-01'
    print(first_day_of_month)
    cursor = db.get_cursor()
    cursor.execute("SELECT SUM(amount) "
                   f"FROM expense "
                   f"WHERE date(created) >= '{first_day_of_month}'")
    result__total_month = cursor.fetchone()
    print(result__total_month)
    cursor.execute(f"SELECT name, SUM(amount), date(created) "
                   f"FROM expense " 
                   f"JOIN category ON codename=category_codename "
                   f"GROUP BY name, date(created) "
                   f"HAVING date(created) >= '{first_day_of_month}' "
                   f"ORDER BY date(created) ")
    result = cursor.fetchall()
    print(result)
    if not result__total_month:
        return "В этом месяце ещё нет расходов"
    all_today_expenses = ""
    for i in result:
        all_today_expenses += f"{i[0]} — {round(i[1], 2)} руб. - {i[2]}\n"
    cursor.execute(f"SELECT SUM(amount) "
                   f"FROM expense WHERE date(created) >= '{first_day_of_month}' "
                   f"AND category_codename IN (select codename "
                   f"FROM category WHERE is_base_expense=true)")
    result = cursor.fetchone()
    base_today_expenses = result[0] if result[0] else 0
    return (f"Расходы в текущем месяце:\n"
            f"всего — {result__total_month[0]} руб., из них:\n"
            f"{all_today_expenses}\n"
            f"базовые — {base_today_expenses} руб. из "
            f"{now.day * _get_budget_limit()} руб.\n"
            f"остаток - {now.day * _get_budget_limit() - base_today_expenses} руб.")


def last() -> List[Expense]:
    """Возвращает последние несколько расходов"""
    cursor = db.get_cursor()
    cursor.execute(
        "SELECT e.id, e.amount, c.name "
        "FROM expense e LEFT JOIN category c "
        "ON c.codename=e.category_codename "
        "ORDER BY created DESC limit 10")
    rows = cursor.fetchall()
    last_expenses = [Expense(id=row[0], amount=row[1], category_name=row[2]) for row in rows]
    return last_expenses


def delete_expense(row_id: int) -> None:
    """Удаляет сообщение по его идентификатору"""
    db.delete("expense", row_id)


def _parse_message(raw_message: str) -> Message:
    """Парсит текст пришедшего сообщения о новом расходе."""
    regexp_result = re.findall(r"\s(\d*\.?,?\d{,2}р?)\s(\w*\d*\.?\w*\d*).*", raw_message)
    if not regexp_result:
        regexp_result = re.findall(r"(\d*\.?,?\d{,2}р?)\s(\w*\d*\.?\w*\d*).*", raw_message)
    print(regexp_result)
    if not regexp_result or not regexp_result[0][0] \
            or not regexp_result[0][1]:
        raise exceptions.NotCorrectMessage(
            "Не могу понять сообщение. Напишите сообщение в формате, "
            "например:\n1500р метро")

    amount = regexp_result[0][0].replace(" ", "").replace("р", "").replace(",", ".")
    category_text = regexp_result[0][1].strip().lower()
    return Message(amount=amount, category_text=category_text)


def _get_now_formatted() -> str:
    """Возвращает сегодняшнюю дату строкой"""
    return _get_now_datetime().strftime("%Y-%m-%d %H:%M:%S")


def _get_now_datetime() -> datetime.datetime:
    """Возвращает сегодняшний datetime с учётом времненной зоны Мск."""
    tz = pytz.timezone("Asia/Novosibirsk")
    now = datetime.datetime.now(tz)
    return now


def _get_budget_limit() -> int:
    """Возвращает дневной лимит трат для основных базовых трат"""
    return db.fetchall("budget", ["daily_limit"])[0]["daily_limit"]
