from aiofiles import tempfile
from aiogram import Dispatcher, Router, F
from aiogram.filters import CommandStart, CommandObject, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile
from aiohttp import ClientError
from dateutil.relativedelta import relativedelta

from cybernexvpn.cybernexvpn_bot.bot.keyboards.keyboards import *
from cybernexvpn.cybernexvpn_bot.bot.models import PaymentModel
from cybernexvpn.cybernexvpn_bot.bot.utils import states
from cybernexvpn.cybernexvpn_bot.bot.utils.client_utils.clients import (
    get_user_clients,
    create_client,
    get_config_file,
    get_client,
    patch_client,
    delete_client,
    reactivate_client,
)
from cybernexvpn.cybernexvpn_bot.bot.utils.client_utils.payments import (
    get_transactions_history,
    gen_payment_url,
)
from cybernexvpn.cybernexvpn_bot.bot.utils.client_utils.promo_codes import (
    apply_promo_code,
)
from cybernexvpn.cybernexvpn_bot.bot.utils.client_utils.servers import (
    get_servers,
    get_server,
)
from cybernexvpn.cybernexvpn_bot.bot.utils.client_utils.users import (
    get_or_create_user,
    apply_invitation_request,
    get_user,
)
from cybernexvpn.cybernexvpn_bot.bot.utils.common import *
from cybernexvpn.cybernexvpn_bot.bot.utils.common import get_client_data
from cybernexvpn.cybernexvpn_bot.bot.utils.filters import MainMenuFilter
from cybernexvpn.cybernexvpn_bot import config

dp = Dispatcher()
router = Router()
dp.include_router(router)


# COMMON FUNCTIONS


@dp.message(CommandStart())
async def welcome_message(message: Message, command: CommandObject):
    user_id = message.chat.id
    user, created = await get_or_create_user(user_id, message.from_user.username)

    if created and (inviter_id := command.args):
        try:
            inviter_id = int(inviter_id)
            if await apply_invitation_request(message.from_user.id, inviter_id):
                await send_safely(
                    inviter_id,
                    text=new_text_storage.SUCCESSFUL_INVITATION_INFO_MSG.format(
                        f"@{message.from_user.username}"
                        if message.from_user.username
                        else ""
                    ),
                )
        except ValueError | ClientError:
            pass

    if created:
        reply_markup = get_first_usage_keyboard()
        text = new_text_storage.FIRST_USAGE_TEXT
    else:
        reply_markup = get_main_menu_keyboard()
        text = new_text_storage.MAIN_MENU_TEXT

    await message.answer(text, reply_markup=reply_markup)


@router.message(Command("menu"))
async def handle_main_menu_callback(message: Message):
    await message.answer(
        text=new_text_storage.MAIN_MENU_TEXT,
        reply_markup=get_main_menu_keyboard(),
    )


@router.callback_query(MainMenuFilter())
async def handle_main_menu_callback(call: CallbackQuery):
    text = new_text_storage.MAIN_MENU_TEXT
    keyboard = get_main_menu_keyboard()

    if call.data != ButtonsStorage.GO_BACK_TO_MAIN_MENU_WITH_NEW_MESSAGE.callback:
        await call.message.edit_text(
            text=text,
            reply_markup=keyboard,
        )
        return

    await call.message.delete_reply_markup()
    await call.message.answer(
        text=text,
        reply_markup=keyboard,
    )


@router.callback_query(F.data == ButtonsStorage.CANCEL_STATE.callback)
async def handle_cancel_state_query(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        new_text_storage.MAIN_MENU_TEXT, reply_markup=get_main_menu_keyboard()
    )


# DEVICES


@router.callback_query(F.data == ButtonsStorage.DEVICES.callback)
async def handle_callback(call: CallbackQuery):
    clients = await get_user_clients(user_id=call.from_user.id)
    await call.message.edit_text(
        text=(
            new_text_storage.CHOOSE_DEVICE
            if clients
            else new_text_storage.NO_DEVICES_ADDED
        ),
        reply_markup=get_devices_keyboard(clients),
    )


@router.callback_query(
    DevicesCallbackFactory.filter(F.callback == ButtonsStorage.DEVICE.callback)  # noqa
)
async def handle_specific_device_query(
    call: CallbackQuery, callback_data: DevicesCallbackFactory
):
    client_id = callback_data.id
    client = await get_client(call.from_user.id, client_id)

    data = await get_client_data(client)

    text = new_text_storage.SPECIFIC_ACTIVE_DEVICE_INFO_TEXT
    if not client.is_active:
        text = new_text_storage.SPECIFIC_INACTIVE_DEVICE_INFO_TEXT
        data["date"] = (client.end_date + relativedelta(months=2)).strftime("%d.%m.%Y")

    text = text.format(**data)
    await call.message.edit_text(
        text=text,
        reply_markup=get_specific_device_keyboard(client),
        parse_mode="HTML",
    )


# # noinspection PyTypeChecker
# @router.callback_query(
#     DevicesCallbackFactory.filter(
#         F.callback == ButtonsStorage.GET_DEVICES_CONFIG_AND_QR.callback
#     )
# )
# tasks def handle_get_device_config_and_qr_query(
#     call: CallbackQuery, callback_data: DevicesCallbackFactory
# ):
#     device_num = callback_data.device_num
#     client = await db_manager.get_record(
#         Client, user_id=call.from_user.id, device_num=device_num
#     )
#     wg_client = await get_wg_client_by_client(client)
#     await send_config_and_qr(wg_client, call, client.device_num)
#
#
# noinspection PyTypeChecker


@router.callback_query(
    DevicesCallbackFactory.filter(
        F.callback == ButtonsStorage.REACTIVATE_DEVICE.callback
    )
)
async def handle_reactivate_device_query(
    call: CallbackQuery, callback_data: DevicesCallbackFactory
):
    client = await get_client(call.from_user.id, callback_data.id)
    client_was_active = client.is_active

    if not client.is_active:
        user = await get_user(call.from_user.id)
        if user.balance < client.price:
            await call.answer(
                new_text_storage.NOT_ENOUGH_MONEY_ERROR_MSG.format(user.balance),
                show_alert=True,
            )
            return

        client = await reactivate_client(call.from_user.id, client.id)

        await call.message.edit_text(
            new_text_storage.DEVICE_SUCCESSFULLY_REACTIVATED.format(client.price),
        )

    data = await get_client_data(client)
    text = new_text_storage.SPECIFIC_ACTIVE_DEVICE_INFO_TEXT
    text = text.format(**data)

    if client_was_active:
        await call.message.edit_text(
            text=text,
            reply_markup=get_specific_device_keyboard(client),
            parse_mode="HTML",
        )
        notification = new_text_storage.DEVICE_ALREADY_ACTIVE
        await call.answer(notification)
        return

    await call.bot.send_message(
        chat_id=call.from_user.id,
        text=text,
        reply_markup=get_specific_device_keyboard(client),
        parse_mode="HTML",
    )


# ADDING DEVICES


@router.callback_query(F.data == ButtonsStorage.ADD_DEVICE.callback)
async def handle_query(call: CallbackQuery):
    servers = await get_servers()
    if not servers:
        text = new_text_storage.NO_SERVERS_AVAILABLE
        keyboard = None
    else:
        text = new_text_storage.CHOOSE_REGION
        keyboard = get_servers_keyboard(servers)

    await call.message.edit_text(
        text=text,
        reply_markup=keyboard,
    )


@router.callback_query(
    ServersCallbackFactory.filter(F.callback == ButtonsStorage.SERVER.callback)  # noqa
)
async def handle_choose_server_query(
    call: CallbackQuery, callback_data: ServersCallbackFactory
):
    server_id = callback_data.id
    server = await get_server(server_id)
    if not server:
        await call.message.edit_text(
            text=new_text_storage.SERVER_NOT_FOUND_ERROR_MSG,
            reply_markup=get_back_to_main_menu_keyboard(),
        )
        return

    await call.message.edit_text(
        text=new_text_storage.SERVER_DESCRIPTION.format(
            server.name,
            server.price,
        ),
        reply_markup=get_specific_server_keyboard(server),
    )


@router.callback_query(AddDeviceFactory.filter(F.type == None))  # noqa
async def handle_add_device_choose_type_query(
    call: CallbackQuery, callback_data: AddDeviceFactory
):
    server = await get_server(callback_data.id)
    user = await get_user(call.from_user.id)

    if not server:
        await call.message.edit_text(
            new_text_storage.SERVER_NOT_FOUND_ERROR_MSG,
            reply_markup=get_back_to_main_menu_keyboard(),
        )
        return

    if user.balance < server.price:
        await call.answer(
            new_text_storage.NOT_ENOUGH_MONEY_ERROR_MSG.format(user.balance),
            show_alert=True,
        )
        return

    choose_device_type_keyboard = get_choose_device_type_keyboard(server=server)
    await call.message.edit_text(
        text=new_text_storage.CHOOSE_DEVICE_TYPE,
        reply_markup=choose_device_type_keyboard,
    )


@router.callback_query(AddDeviceFactory.filter())
async def handle_add_device_query(call: CallbackQuery, callback_data: AddDeviceFactory):
    client = await create_client(
        call.from_user.id, callback_data.id, callback_data.type
    )
    if not client:
        # todo
        await call.message.edit_text(
            new_text_storage.SOMETHING_WENT_WRONG_ERROR_MSG,
            reply_markup=get_back_to_main_menu_keyboard(),
        )
        return

    await call.message.edit_text(
        new_text_storage.DEVICE_SUCCESSFULLY_ADDED,
    )

    config_file_data = await get_config_file(
        user_id=call.from_user.id, client_id=client.id
    )

    async with tempfile.NamedTemporaryFile(
        mode="w+", delete=True, dir="/"
    ) as temp_file:
        await temp_file.write(config_file_data)
        await temp_file.flush()

        await call.bot.send_document(
            chat_id=call.from_user.id,
            document=FSInputFile(temp_file.name, filename=f"{client.name}.conf"),
        )


# EDITING DEVICES


@router.callback_query(
    DevicesCallbackFactory.filter(
        F.callback == ButtonsStorage.EDIT_DEVICE.callback  # noqa
    )
)
async def handle_specific_device_query(
    call: CallbackQuery, callback_data: DevicesCallbackFactory
):
    client_id = callback_data.id
    client = await get_client(call.from_user.id, client_id)

    data = await get_client_data(client)

    text = (
        new_text_storage.EDIT_ACTIVE_DEVICE_TEXT
        if client.is_active
        else new_text_storage.EDIT_INACTIVE_DEVICE_TEXT
    )
    text = text.format(**data)

    await call.message.edit_text(
        text=text,
        reply_markup=get_edit_device_keyboard(client),
        parse_mode="HTML",
    )


@router.callback_query(
    DevicesCallbackFactory.filter(
        F.callback == ButtonsStorage.EDIT_DEVICE_AUTO_RENEW.callback  # noqa
    )
)
async def handle_edit_auto_renew_query(
    call: CallbackQuery, callback_data: DevicesCallbackFactory
):
    client = await get_client(call.from_user.id, callback_data.id)
    client = await patch_client(
        call.from_user.id, client.id, auto_renew=not client.auto_renew
    )

    data = await get_client_data(client)
    text = (
        new_text_storage.EDIT_ACTIVE_DEVICE_TEXT
        if client.is_active
        else new_text_storage.EDIT_INACTIVE_DEVICE_TEXT
    )
    text = text.format(**data)

    await call.message.edit_text(
        text=text,
        reply_markup=get_edit_device_keyboard(client),
        parse_mode="HTML",
    )

    notification = (
        new_text_storage.AUTO_RENEW_ON
        if client.auto_renew
        else new_text_storage.AUTO_RENEW_OFF
    )
    await call.answer(notification)


@router.callback_query(
    DevicesCallbackFactory.filter(
        F.callback == ButtonsStorage.EDIT_DEVICE_TYPE.callback  # noqa
    )
)
async def handle_edit_device_type_query(
    call: CallbackQuery, callback_data: DevicesCallbackFactory
):
    client = await get_client(call.from_user.id, callback_data.id)
    await call.message.edit_text(
        text=new_text_storage.CHOOSE_DEVICE_TYPE,
        reply_markup=get_choose_device_type_keyboard(client=client),
    )


@router.callback_query(EditDeviceTypeCallbackFactory.filter())
async def handle_set_device_type_query(
    call: CallbackQuery, callback_data: EditDeviceTypeCallbackFactory
):
    client = await patch_client(
        call.from_user.id, callback_data.id, type=callback_data.type
    )

    data = await get_client_data(client)

    text = new_text_storage.SPECIFIC_ACTIVE_DEVICE_INFO_TEXT
    if not client.is_active:
        text = new_text_storage.SPECIFIC_INACTIVE_DEVICE_INFO_TEXT
        data["date"] = (client.end_date + relativedelta(months=2)).strftime("%d.%m.%Y")

    await call.message.edit_text(
        text=text.format(**data),
        reply_markup=get_specific_device_keyboard(client),
        parse_mode="HTML",
    )

    await call.answer(new_text_storage.DEVICE_TYPE_SUCCESSFULLY_CHANGED)


@router.callback_query(
    DevicesCallbackFactory.filter(
        F.callback == ButtonsStorage.EDIT_DEVICE_NAME.callback  # noqa
    )
)
async def handle_edit_device_auto_renew_query(
    call: CallbackQuery, callback_data: DevicesCallbackFactory, state: FSMContext
):
    await state.set_state(states.EDIT_DEVICE_NAME_EXPECTING_STATE)
    await state.set_data({"message": call.message, "client_id": callback_data.id})

    await call.message.edit_text(
        text=new_text_storage.INPUT_NEW_DEVICE_NAME,
        reply_markup=get_cancel_state_keyboard(),
    )


@router.message(states.EDIT_DEVICE_NAME_EXPECTING_STATE)
async def handle_message(message: Message, state: FSMContext):
    state_data = await state.get_data()
    msg_to_edit: Message = state_data["message"]
    await state.clear()

    try:
        await msg_to_edit.edit_text(
            text=new_text_storage.DEVICE_SUCCESSFULLY_RENAMED, reply_markup=None
        )
    except Exception:
        pass

    await patch_client(message.from_user.id, state_data["client_id"], name=message.text)
    clients = await get_user_clients(message.from_user.id)

    text = (
        new_text_storage.CHOOSE_DEVICE if clients else new_text_storage.NO_DEVICES_ADDED
    )

    await message.answer(
        text=text,
        reply_markup=get_devices_keyboard(clients),
        parse_mode="HTML",
    )


# DELETING DEVICES


@router.callback_query(
    DevicesCallbackFactory.filter(
        F.callback == ButtonsStorage.DELETE_DEVICE.callback  # noqa
    )
)
async def handle_query(call: CallbackQuery, callback_data: DevicesCallbackFactory):
    client = await get_client(call.from_user.id, callback_data.id)
    if not client:
        await call.message.edit_text(
            text=new_text_storage.CLIENT_NOT_FOUND_ERROR_MSG,
            reply_markup=get_back_to_main_menu_keyboard(),
        )
        return

    await call.message.edit_text(
        text=new_text_storage.DELETE_DEVICE_CONFIRMATION_INFO,
        reply_markup=get_delete_device_confirmation_keyboard(client),
    )


@router.callback_query(
    DevicesCallbackFactory.filter(
        F.callback == ButtonsStorage.DELETE_DEVICE_CONFIRMATION.callback  # noqa
    )
)
async def handle_delete_device_confirmation_query(
    call: CallbackQuery, callback_data: DevicesCallbackFactory
):
    await delete_client(call.from_user.id, callback_data.id)
    # todo
    await call.message.edit_text(
        new_text_storage.DEVICE_SUCCESSFULLY_DELETED,
        reply_markup=get_back_to_main_menu_keyboard(),
    )


# FINANCE


@router.callback_query(F.data == ButtonsStorage.FINANCE.callback)
async def handle_finance_callback_query(call: CallbackQuery):
    user = await get_user(call.from_user.id)
    await call.message.edit_text(
        new_text_storage.BALANCE_INFO.format(user.balance),
        reply_markup=get_finance_callback(),
    )


@router.callback_query(F.data == ButtonsStorage.GET_TRANSACTIONS_HISTORY.callback)
async def handle_get_transactions_query(call: CallbackQuery):
    file_data = await get_transactions_history(call.from_user.id)
    if not file_data:
        await call.message.edit_text(
            new_text_storage.SOMETHING_WENT_WRONG_ERROR_MSG,
            reply_markup=get_back_to_main_menu_keyboard(),
        )
        return

    await delete_message_or_delete_markup(call.message)

    async with tempfile.NamedTemporaryFile(
        mode="w+", delete=True, dir="/"
    ) as temp_file:
        await temp_file.write(file_data)
        await temp_file.flush()

        await call.bot.send_document(
            chat_id=call.from_user.id,
            document=FSInputFile(temp_file.name, filename="Transactions.txt"),
        )

    await call.message.answer(
        new_text_storage.MAIN_MENU_TEXT, reply_markup=get_main_menu_keyboard()
    )


@router.callback_query(F.data == ButtonsStorage.FILL_UP_BALANCE.callback)
async def handle_fill_up_balance_query(call: CallbackQuery):
    from_admin = call.from_user.id == config.ADMIN_USER_ID
    await call.message.edit_text(
        new_text_storage.CHOOSE_SUM_TO_FILL_UP_BALANCE,
        reply_markup=get_fill_up_balance_keyboard(from_admin),
    )


@router.callback_query(FillUpBalanceFactory.filter())
async def handle_fill_up_balance_factory_query(
    call: CallbackQuery, callback_data: FillUpBalanceFactory
):
    url = await gen_payment_url(call.from_user.id, callback_data.value)
    if not url:
        await call.message.edit_text(
            new_text_storage.SOMETHING_WENT_WRONG_ERROR_MSG,
            reply_markup=get_back_to_main_menu_keyboard(),
        )
        return

    save_payment_to_redis(
        url,
        payment=PaymentModel(
            user_id=call.from_user.id,
            message_id=call.message.message_id,
            value=callback_data.value,
        ),
    )

    await call.message.edit_text(
        new_text_storage.FILL_UP_BALANCE_INFO_MSG.format(callback_data.value),
        reply_markup=get_payment_url_keyboard(url),
    )


# Promo Codes


@router.callback_query(F.data == ButtonsStorage.PROMO_CODE.callback)
async def handle_promo_code_query(call: CallbackQuery, state: FSMContext):
    await state.set_state(states.PROMO_CODE_EXPECTING_STATE)
    await state.set_data({"message": call.message})
    await call.message.edit_text(
        new_text_storage.INPUT_PROMO_CODE, reply_markup=get_cancel_state_keyboard()
    )


@router.message(states.PROMO_CODE_EXPECTING_STATE)
async def handle_message(message: Message, state: FSMContext):
    state_data = await state.get_data()
    msg_to_edit: Message = state_data["message"]
    await state.clear()

    applied: schemas.ApplyPromoCodeResponse | None = await apply_promo_code(
        message.from_user.id, promo_code=message.text.strip()
    )

    try:
        await msg_to_edit.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    if applied:
        await message.answer(
            text=new_text_storage.PROMO_CODE_SUCCESSFULLY_APPLIED.format(applied.value),
            reply_markup=get_back_to_main_menu_keyboard(),
        )
    else:  # todo
        await message.answer(
            text=new_text_storage.PROMO_CODE_NOT_FOUND_ERROR_MSG,
            reply_markup=get_back_to_main_menu_keyboard(),
        )


@router.callback_query(F.data == ButtonsStorage.INVITATION_LINK.callback)
async def handle_invitation_link_query(call: CallbackQuery):
    user_link = generate_invitation_link(call.from_user.id)
    await call.message.edit_text(
        new_text_storage.INVITATION_LINK_INFO_MSG.format(user_link),
        reply_markup=get_back_to_main_menu_keyboard(),
    )
