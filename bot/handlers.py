import logging
from datetime import datetime
from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from bot.buttons import get_main_menu, get_user_options, get_user_list_keyboard, get_cities
from db.model import Birthday
from conf import ADMIN_USER_ID


router = Router()
logging.basicConfig(level=logging.INFO)


class AddUserForm(StatesGroup):
    name = State()
    birthdate = State()


class EditUserForm(StatesGroup):
    new_name = State()
    new_birthdate = State()


class SearchUserForm(StatesGroup):
    name = State()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(f"Hello {message.from_user.first_name + (message.from_user.last_name if message.from_user.last_name else '')}")


@router.message(Command("admin"), F.from_user.id == ADMIN_USER_ID)
async def cmd_admin(message: Message):
    await message.answer("Welcome to the Admin Panel.", reply_markup=get_main_menu())


@router.message(F.text == "Add User", F.from_user.id == ADMIN_USER_ID)
async def add_user_start(message: Message, state: FSMContext):
    await message.answer("Please enter the user's name:")
    await state.set_state(AddUserForm.name)


@router.message(AddUserForm.name)
async def add_user_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Please enter the user's birthdate (YYYY-MM-DD):")
    await state.set_state(AddUserForm.birthdate)


@router.message(AddUserForm.birthdate)
async def add_user_birthdate(message: Message, state: FSMContext, bot: Bot):
    birthdate = message.text
    user_data = await state.get_data()
    name = user_data['name']

    # Validate birthdate format
    try:
        datetime.strptime(birthdate, "%Y-%m-%d")
    except ValueError:
        await message.answer("Invalid date format. Please enter date as YYYY-MM-DD:")
        return

    await Birthday(name=name, birthdate=birthdate).save()
    await message.answer(f"User '{name}' with birthday '{birthdate}' added successfully! 🎉")

    # Check if today is the user's birthday and send congrats immediately
    if datetime.now().strftime("%Y-%m-%d") == birthdate:
        await bot.send_message(message.chat.id, f"🎉 Happy Birthday, {name}! 🎂")

    await state.clear()


@router.message(F.text == "Search User", F.from_user.id == ADMIN_USER_ID)
async def search_user_start(message: Message, state: FSMContext):
    await message.answer("Please enter the name of the user you want to search for:")
    await state.set_state(SearchUserForm.name)


@router.message(SearchUserForm.name)
async def search_user_name(message: Message, state: FSMContext):
    name = message.text
    users = await Birthday().search_user_by_name(name)
    if users:
        await message.answer("Select a user:", reply_markup=get_user_list_keyboard(users))
    else:
        await message.answer(f"No users found with the name containing '{name}'.")
    await state.clear()


@router.callback_query(F.data.startswith("edit_"))
async def edit_user(call: CallbackQuery, state: FSMContext):
    user_id = call.data.split("_")[1]
    await state.update_data(user_id=user_id)
    await call.message.edit_text("Please enter the new name for the user:")
    await state.set_state(EditUserForm.new_name)


@router.message(EditUserForm.new_name)
async def edit_user_name(message: Message, state: FSMContext):
    await state.update_data(new_name=message.text)
    await message.answer("Please enter the new birthdate (YYYY-MM-DD):")
    await state.set_state(EditUserForm.new_birthdate)


@router.message(EditUserForm.new_birthdate)
async def edit_user_birthdate(message: Message, state: FSMContext, bot: Bot):
    birthdate = message.text
    user_data = await state.get_data()
    new_name = user_data['new_name']
    user_id = user_data['user_id']

    # Validate birthdate format
    try:
        datetime.strptime(birthdate, "%Y-%m-%d")
    except ValueError:
        await message.answer("Invalid date format. Please enter date as YYYY-MM-DD:")
        return

    user = await Birthday(id=int(user_id)).update(name=new_name, birthdate=birthdate)
    await message.answer(f"User '{user.name}' updated successfully! 🎉")

    # Check if today is the user's birthday and send congrats immediately
    if datetime.now().strftime("%Y-%m-%d") == birthdate:
        await bot.send_message(message.chat.id, f"🎉 Happy Birthday, {user.name}! 🎂")

    await state.clear()


@router.callback_query(F.data.startswith("delete_"))
async def delete_user_callback(call: CallbackQuery):
    user_id = call.data.split("_")[1]
    await Birthday().delete(user_id)
    await call.message.edit_text(f"User has been deleted successfully.")


@router.message(F.text == "User List", F.from_user.id == ADMIN_USER_ID)
async def user_list(message: Message):
    users = await Birthday().objects
    if users:
        await message.answer("User List:", reply_markup=get_user_list_keyboard(users))
    else:
        await message.answer("The user list is empty.")


@router.callback_query(F.data.startswith("view_"))
async def view_user_callback(call: CallbackQuery):
    user_id = call.data.split("_")[1]
    user = await Birthday().get_user_by_id(user_id)
    if user:
        await call.message.edit_text(
            f"User Details:\n\nName: {user.name}\nBirthdate: {user.birthdate}",
            reply_markup=get_user_options(user_id)
        )
    else:
        await call.message.edit_text(f"User not found.")




