import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
import config
import database

database.init_db()

bot = Bot(token=config.TOKEN)
dp = Dispatcher()

ADMINS = config.ADMINS

def is_admin(user_id):
    return user_id in ADMINS

def get_menu_keyboard():
    items = database.get_menu()
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for item in items:
        kb.add(KeyboardButton(f"{item[1]} — {item[2]} руб."))
    kb.add(KeyboardButton("Готово"))
    return kb

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Добро пожаловать! Введите ваше имя:")

@dp.message()
async def handle_name(message: types.Message):
    if not hasattr(message, "client_data"):
        message.client_data = {}
    message.client_data["name"] = message.text
    await message.answer("Введите последние 4 цифры вашей карты лояльности:")

@dp.message()
async def handle_card(message: types.Message):
    if len(message.text) != 4 or not message.text.isdigit():
        await message.answer("Введите ровно 4 цифры!")
        return
    message.client_data["card"] = message.text
    await message.answer("Выберите товары из меню:", reply_markup=get_menu_keyboard())

@dp.message()
async def handle_order(message: types.Message):
    if message.text == "Готово":
        items = message.client_data.get("items", [])
        if not items:
            await message.answer("Вы ничего не выбрали!")
            return
        order_id = database.add_order(
            message.client_data["name"],
            message.client_data["card"],
            ", ".join(items)
        )
        await message.answer(f"Заказ #{order_id} принят! Статус: новый")
        for admin in ADMINS:
            try:
                await bot.send_message(
                    admin,
                    f"🆕 Новый заказ #{order_id}\n"
                    f"Имя: {message.client_data['name']}\n"
                    f"Карта: {message.client_data['card']}\n"
                    f"Товары: {', '.join(items)}"
                )
            except:
                pass
        return
    if "items" not in message.client_data:
        message.client_data["items"] = []
    message.client_data["items"].append(message.text)
    await message.answer(f"Добавлено: {message.text}")

@dp.message(Command("add_item"))
async def add_item(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    try:
        parts = message.text.split(maxsplit=2)
        name = parts[1]
        price = float(parts[2])
        database.add_menu_item(name, price)
        await message.answer(f"Товар '{name}' добавлен!")
    except:
        await message.answer("Используйте: /add_item Название Цена")

@dp.message(Command("remove_item"))
async def remove_item(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    try:
        item_id = int(message.text.split()[1])
        database.remove_menu_item(item_id)
        await message.answer(f"Товар #{item_id} удалён!")
    except:
        await message.answer("Используйте: /remove_item ID")

@dp.message(Command("menu"))
async def show_menu(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    items = database.get_menu()
    if not items:
        await message.answer("Меню пустое.")
        return
    text = "🍽️ Меню:\n"
    for item in items:
        text += f"{item[0]}. {item[1]} — {item[2]} руб.\n"
    await message.answer(text)

@dp.message(Command("history"))
async def history(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    orders = database.get_orders()
    if not orders:
        await message.answer("Заказов пока нет.")
        return
    text = "📋 История заказов:\n"
    for order in orders:
        text += f"#{order[0]} | {order[1]} | {order[2]} | {order[3]} | {order[4]} | {order[5]}\n"
    await message.answer(text)

@dp.message(Command("status"))
async def change_status(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    try:
        parts = message.text.split()
        order_id = int(parts[1])
        status = parts[2]
        if status not in ["новый", "принят", "готов"]:
            await message.answer("Статус должен быть: новый, принят или готов")
            return
        database.update_order_status(order_id, status)
        await message.answer(f"Заказ #{order_id} → {status}")
    except:
        await message.answer("Используйте: /status ID статус")

async def main():
    port = int(os.environ.get("PORT", 8080))
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
