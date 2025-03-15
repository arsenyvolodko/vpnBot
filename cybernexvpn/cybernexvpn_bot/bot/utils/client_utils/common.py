from aiogram.types import CallbackQuery, Message

from cybernexvpn.cybernexvpn_bot.bot.keyboards.keyboards import get_back_to_main_menu_keyboard


async def edit_with_error(call: CallbackQuery | Message, error: str) -> None:
    if isinstance(call, CallbackQuery):
        await call.message.edit_text(error, reply_markup=get_back_to_main_menu_keyboard())
    elif isinstance(call, Message):
        message = call
        await message.edit_reply_markup(
            reply_markup=None
        )
        await message.bot.send_message(
            chat_id=message.chat.id,
            text=error,
            reply_markup=get_back_to_main_menu_keyboard()
        )
