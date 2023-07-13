from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

button_today = KeyboardButton('Траты за день')
button_month = KeyboardButton('Траты за месяц')
button_expenses = KeyboardButton('Последние траты')
button_categories = KeyboardButton('Категории трат')

markup_main = ReplyKeyboardMarkup(resize_keyboard=True).row(
    button_today, button_month).row(button_expenses, button_categories)
