import datetime

from aiogram import Dispatcher, Router, F
from aiogram.filters import CommandStart, CommandObject, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, CallbackQuery, Message

from vpnBot import config
from vpnBot.db import db_manager
from vpnBot.db.tables import User, Transaction
from vpnBot.enums import OperationTypeEnum, TransactionCommentEnum
from vpnBot.exceptions.clients.client_base_error import ClientBaseError
from vpnBot.exceptions.promo_codes.promo_code_base_error import PromoCodeBaseError
from vpnBot.keyboards.keyboards import *
from vpnBot.consts import states
from vpnBot.consts.common import *
from vpnBot.consts.texts_storage import *
from vpnBot.utils.bot_funcs import (
    get_user_balance,
    get_wg_client_by_client,
    send_config_and_qr,
    process_transaction,
    generate_invitation_link,
    check_invitation,
)
from vpnBot.utils.files import delete_file
from vpnBot.utils.filters import MainMenuFilter

dp = Dispatcher()
router = Router()
dp.include_router(router)


@dp.message(CommandStart())
async def welcome_message(message: Message, command: CommandObject):
    user = await db_manager.get_record(User, message.from_user.id)

    if not user:
        if inviter_id := command.args:
            await check_invitation(message, inviter_id)

        new_user = User(id=message.from_user.id, username=message.from_user.username)
        user = await db_manager.add_record(new_user)
        new_transaction = Transaction(
            user_id=user.id,
            value=PRICE,
            operation_type=OperationTypeEnum.INCREASE,
            comment=TransactionCommentEnum.START_BALANCE,
        )
        await db_manager.add_record(new_transaction)

    await message.answer(TextsStorage.START_TEXT, reply_markup=get_start_keyboard())


@router.message(Command("menu"))
async def handle_main_menu_callback(message: Message):
    await message.bot.send_message(
        message.from_user.id,
        text=TextsStorage.MAIN_MENU_TEXT,
        reply_markup=get_main_menu_keyboard(),
    )


@router.callback_query(MainMenuFilter())
async def handle_main_menu_callback(call: CallbackQuery):
    await call.message.edit_text(
        text=TextsStorage.MAIN_MENU_TEXT,
        reply_markup=get_main_menu_keyboard(),
    )


@router.callback_query(F.data == ButtonsStorage.DEVICES.callback)
async def handle_callback(call: CallbackQuery):
    user_devices = await db_manager.get_user_devices(call.from_user.id)
    await call.message.edit_text(
        text=(
            TextsStorage.CHOOSE_DEVICE
            if user_devices
            else TextsStorage.NO_DEVICES_ADDED
        ),
        reply_markup=get_devices_keyboard(
            user_devices, len(user_devices) < DEVICES_MAX_AMOUNT
        ),
    )


@router.callback_query(F.data == ButtonsStorage.ADD_DEVICE.callback)
async def handle_query(call: CallbackQuery):
    user_balance = await get_user_balance(call.from_user.id)
    await call.message.edit_text(
        text=TextsStorage.ADD_DEVICE_CONFIRMATION_INFO.format(PRICE, user_balance),
        reply_markup=get_add_device_confirmation_keyboard(),
    )


@router.callback_query(F.data == ButtonsStorage.ADD_DEVICE_CONFIRMATION.callback)
async def add_device_confirmed(call: CallbackQuery):
    try:
        client = await db_manager.add_client(call.from_user.id)
        await call.message.answer(TextsStorage.DEVICE_SUCCESSFULLY_ADDED)
        wg_client = await get_wg_client_by_client(client)
        await send_config_and_qr(wg_client, call, client.device_num)
        return
    except ClientBaseError as e:
        text = e.message
    except Exception:
        text = TextsStorage.SOMETHING_WENT_WRONG_ERROR_MSG
    await call.message.edit_text(
        text=text, reply_markup=get_back_to_main_menu_keyboard()
    )


# noinspection PyTypeChecker
@router.callback_query(
    DevicesCallbackFactory.filter(F.callback == ButtonsStorage.DELETE_DEVICE.callback)
)
async def handle_query(call: CallbackQuery, callback_data: DevicesCallbackFactory):
    await call.message.edit_text(
        text=TextsStorage.DELETE_DEVICE_CONFIRMATION_INFO,
        reply_markup=get_delete_device_confirmation_keyboard(
            callback_data.device_num
        )
    )


# noinspection PyTypeChecker
@router.callback_query(
    DevicesCallbackFactory.filter(F.callback == ButtonsStorage.DELETE_DEVICE_CONFIRMATION.callback)
)
async def handle_specific_device_query(
        call: CallbackQuery, callback_data: DevicesCallbackFactory
):
    device_num = callback_data.device_num
    client = await db_manager.get_clint_by_user_id_and_device_num(
        call.from_user.id, device_num
    )
    try:
        await db_manager.delete_client(client)
        text = TextsStorage.DEVICE_SUCCESSFULLY_DELETED
    except Exception:
        text = TextsStorage.SOMETHING_WENT_WRONG_ERROR_MSG
    await call.message.edit_text(
        text,
        reply_markup=get_back_to_main_menu_keyboard(),
    )


# noinspection PyTypeChecker
@router.callback_query(
    DevicesCallbackFactory.filter(
        F.callback == ButtonsStorage.GET_DEVICES_CONFIG_AND_QR.callback
    )
)
async def handle_get_device_config_and_qr_query(
        call: CallbackQuery, callback_data: DevicesCallbackFactory
):
    device_num = callback_data.device_num
    client = await db_manager.get_clint_by_user_id_and_device_num(
        call.from_user.id, device_num
    )
    wg_client = await get_wg_client_by_client(client)
    await send_config_and_qr(wg_client, call, client.device_num)


# noinspection PyTypeChecker
@router.callback_query(
    DevicesCallbackFactory.filter(F.callback == ButtonsStorage.DEVICE.callback)
)
async def handle_specific_device_query(
        call: CallbackQuery, callback_data: DevicesCallbackFactory
):
    device_num = callback_data.device_num
    client = await db_manager.get_clint_by_user_id_and_device_num(
        call.from_user.id, device_num
    )
    status = TextsStorage.ACTIVE if client.active else TextsStorage.INACTIVE
    await call.message.edit_text(
        text=TextsStorage.SPECIFIC_DEVICE_INFO_TEXT.format(
            device_num, status, client.end_date.strftime("%d.%m.%Y")
        ),
        reply_markup=get_specific_device_keyboard(device_num, client.active),
    )


# noinspection PyTypeChecker
@router.callback_query(
    DevicesCallbackFactory.filter(
        F.callback == ButtonsStorage.RESUME_DEVICE_SUBSCRIPTION.callback
    )
)
async def handle_resume_device_subscription_query(
        call: CallbackQuery, callback_data: DevicesCallbackFactory
):
    device_num = callback_data.device_num
    client = await db_manager.get_clint_by_user_id_and_device_num(
        call.from_user.id, device_num
    )
    if not client.active:
        try:
            await db_manager.resume_device_subscription(client.id, call.from_user.id)
            text = TextsStorage.DEVICE_SUBSCRIPTION_SUCCESSFULLY_RESUMED
        except ClientBaseError as e:
            text = e.message
        except Exception:
            text = TextsStorage.SOMETHING_WENT_WRONG_ERROR_MSG
    else:
        text = TextsStorage.DEVICE_SUBSCRIPTION_ALREADY_ACTIVE
    await call.message.edit_text(
        text=text, reply_markup=get_back_to_main_menu_keyboard()
    )


@router.callback_query(F.data == ButtonsStorage.FINANCE.callback)
async def handle_finance_callback_query(call: CallbackQuery):
    user_id = call.from_user.id
    user = await db_manager.get_record(User, user_id)
    await call.message.edit_text(
        TextsStorage.ON_YOUR_ACCOUNT.format(user.balance),
        reply_markup=get_finance_callback(),
    )


@router.callback_query(F.data == ButtonsStorage.GET_TRANSACTIONS_HISTORY.callback)
async def handle_get_transactions_query(call: CallbackQuery):
    user_id = call.from_user.id
    user: User = await db_manager.get_record(User, user_id)
    balance = user.balance
    cur_time = datetime.datetime.now().strftime("%d.%m.%Y, %H:%M")
    text = TextsStorage.CURRENT_BALANCE.format(balance) + "\n\n"
    result = await db_manager.get_user_transactions(user_id)
    for transaction in result:
        cur_transaction = await process_transaction(transaction)
        text += cur_transaction + "\n\n"

    text += TextsStorage.ACTUAL_ON_MOMENT.format(cur_time)

    file_path = config.PATH_TO_CLIENTS_FILES / f"{user_id}_transactions_data.txt"
    with open(file_path, "w") as file:
        file.write(text)
        file.close()

    await call.message.delete()

    await call.bot.send_document(
        chat_id=call.from_user.id,
        document=FSInputFile(file_path, filename="Transactions.txt"),
    )

    await call.message.answer(
        TextsStorage.MAIN_MENU_TEXT, reply_markup=get_main_menu_keyboard()
    )

    await delete_file(file_path)


@router.callback_query(F.data == ButtonsStorage.FILL_UP_BALANCE.callback)
async def handle_fill_up_balance_query(call: CallbackQuery):
    await call.message.edit_text(
        TextsStorage.CHOOSE_SUM_TO_FILL_UP_BALANCE,
        reply_markup=get_fill_up_balance_keyboard(),
    )


@router.callback_query(F.data == ButtonsStorage.PROMO_CODE.callback)
async def handle_promo_code_query(call: CallbackQuery, state: FSMContext):
    await state.set_state(states.PROMO_CODE_EXPECTING_STATE)
    await state.set_data({"message": call.message})
    await call.message.edit_text(
        TextsStorage.INPUT_PROMO_CODE, reply_markup=get_cancel_state_keyboard()
    )


@router.message(states.PROMO_CODE_EXPECTING_STATE)
async def handle_message(message: Message, state: FSMContext):
    state_data = await state.get_data()
    msg_to_edit: Message = state_data["message"]
    await state.clear()
    await msg_to_edit.edit_reply_markup(reply_markup=None)

    try:
        promo_code = await db_manager.add_promo_code_usage(
            message.text.strip(), message.from_user.id
        )
        text = TextsStorage.PROMO_CODE_SUCCESSFULLY_APPLIED.format(promo_code.value)
    except PromoCodeBaseError as e:
        text = e.message
    except Exception:
        text = TextsStorage.SOMETHING_WENT_WRONG_ERROR_MSG

    await message.answer(text=text, reply_markup=get_back_to_main_menu_keyboard())


@router.callback_query(F.data == ButtonsStorage.CANCEL_STATE.callback)
async def handle_cancel_state_query(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        TextsStorage.MAIN_MENU_TEXT, reply_markup=get_main_menu_keyboard()
    )


@router.callback_query(F.data == ButtonsStorage.INVITATION_LINK.callback)
async def handle_invitation_link_query(call: CallbackQuery):
    user_link = generate_invitation_link(call.from_user.id)
    await call.message.edit_text(
        TextsStorage.INVITATION_LINK_INFO_MSG.format(user_link),
        reply_markup=get_back_to_main_menu_keyboard(),
    )


# noinspection PyTypeChecker
@router.callback_query(
    FillUpBalanceFactory.filter(
        F.callback == ButtonsStorage.FILL_UP_BALANCE_VALUE.callback
    )
)
async def handle_fill_up_balance_factory_query(
        call: CallbackQuery, callback_data: FillUpBalanceFactory
):
    updated = await db_manager.update_balance(
        user_id=call.from_user.id,
        value=callback_data.value,
        op_type=OperationTypeEnum.INCREASE,
        comment=TransactionCommentEnum.FILL_UP_BALANCE,
    )

    text = (
        TextsStorage.BALANCE_SUCCESSFULLY_FILLED_UP
        if updated
        else TextsStorage.SOMETHING_WENT_WRONG_ERROR_MSG
    )

    await call.message.edit_text(
        text=text,
        reply_markup=get_back_to_main_menu_keyboard()
    )
