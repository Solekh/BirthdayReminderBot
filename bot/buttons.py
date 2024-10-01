from aiogram.types import InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def get_main_menu():
    rkb = ReplyKeyboardBuilder()
    rkb.add(*[
        KeyboardButton(text="Add User"),
        KeyboardButton(text="Search User"),
        KeyboardButton(text="User List")
    ])
    rkb.adjust(2, 1)
    return rkb.as_markup(resize_keyboard=True)


def get_user_list_keyboard(users):
    """Generate an inline keyboard with a list of users for selection."""
    ikb = InlineKeyboardBuilder()
    ikb.add(*[
        InlineKeyboardButton(text=i.name, callback_data=f"view_{i.id}") for i in users
    ])
    ikb.adjust(2, repeat=True)
    return ikb.as_markup()

def get_user_options(user_id):
    """Create an inline keyboard with options to edit or delete a user, or go back."""
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="Edit", callback_data=f"edit_{user_id}"),
        InlineKeyboardButton(text="Delete", callback_data=f"delete_{user_id}")
    )
    return keyboard.as_markup()

def get_cities(cities):
    ikb = InlineKeyboardBuilder()
    ikb.add(*[
        InlineKeyboardButton(text=i.city, callback_data=f"city_{i.city}") for i in cities
    ])
    ikb.adjust(2, repeat=True)
    return ikb.as_markup()