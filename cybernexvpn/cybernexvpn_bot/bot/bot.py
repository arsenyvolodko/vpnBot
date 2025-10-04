import logging
import os

import qrcode
from aiofiles import tempfile
from aiogram import Dispatcher, Router, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, CommandObject, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, Message
from aiogram.types.callback_query import CallbackQuery
from aiogram.utils.media_group import MediaGroupBuilder
from dateutil.relativedelta import relativedelta

from cybernexvpn.cybernexvpn_bot import config
from cybernexvpn.cybernexvpn_bot.bot.keyboards.buttons_storage import ButtonsStorage
from cybernexvpn.cybernexvpn_bot.bot.keyboards.factories import DevicesCallbackFactory, PostAdditionDeviceFactory, \
    ServersCallbackFactory, AddDeviceFactory, EditDeviceTypeCallbackFactory, FillUpBalanceFactory
from cybernexvpn.cybernexvpn_bot.bot.keyboards.keyboards import get_first_usage_keyboard, get_main_menu_keyboard, \
    get_devices_keyboard, get_specific_device_keyboard, get_choose_device_type_keyboard, \
    get_post_adding_device_keyboard, get_back_to_main_menu_keyboard, get_servers_keyboard, get_specific_server_keyboard, \
    get_edit_device_keyboard, get_cancel_state_keyboard, get_delete_device_confirmation_keyboard, get_finance_callback, \
    get_fill_up_balance_values_keyboard, get_payment_url_keyboard
from cybernexvpn.cybernexvpn_bot.bot.models import PaymentModel
from cybernexvpn.cybernexvpn_bot.bot.states import states
from cybernexvpn.cybernexvpn_bot.bot.utils import new_text_storage
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
    get_servers, get_server,
)
from cybernexvpn.cybernexvpn_bot.bot.utils.client_utils.users import (
    get_or_create_user,
    apply_invitation_request, get_user,
)
from cybernexvpn.cybernexvpn_bot.bot.utils.common import send_safely, get_client_data, \
    check_user_balance_for_new_client, edit_safely, delete_message_or_delete_markup, save_payment_to_redis, \
    generate_invitation_link, get_filename
from cybernexvpn.cybernexvpn_bot.bot.filters import MainMenuFilter
from cybernexvpn.cybernexvpn_client import schemas
from cybernexvpn.cybernexvpn_client.enums import ClientTypeEnum

dp = Dispatcher()
router = Router()
dp.include_router(router)

logger = logging.getLogger(__name__)


# COMMON FUNCTIONS


@dp.message(CommandStart())
async def welcome_message(message: Message, command: CommandObject):
    user_id = message.chat.id
    user, created = await get_or_create_user(user_id, message.from_user.username, message)
    if not user:
        return

    if created and (inviter_id := command.args):
        try:
            inviter_id = int(inviter_id)
        except ValueError:
            pass

        if await apply_invitation_request(message.from_user.id, inviter_id, message):
            await send_safely(
                inviter_id,
                text=new_text_storage.SUCCESSFUL_INVITATION_INFO_MSG.format(
                    f"@{message.from_user.username}"
                    if message.from_user.username
                    else ""
                ),
            )

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

        if call.message.photo:
            await call.message.delete()

            await call.message.answer(
                text=text,
                reply_markup=keyboard,
            )
            return

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
    clients = await get_user_clients(call.from_user.id, call)
    if clients is None:
        return

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
    client = await get_client(call.from_user.id, client_id, call)

    if not client:
        return

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


@router.callback_query(
    DevicesCallbackFactory.filter(
        F.callback == ButtonsStorage.GET_CONNECTION_DATA.callback  # noqa
    )
)
async def handle_get_connection_data_query(
        call: CallbackQuery, callback_data: DevicesCallbackFactory
):
    client = await get_client(call.from_user.id, callback_data.id, call)
    if not client:
        return

    if client.type == ClientTypeEnum.UNKNOWN:
        await call.message.edit_text(
            new_text_storage.SET_CORRECT_DEVICE_TYPE,
            reply_markup=get_choose_device_type_keyboard(client=client),
        )
        return

    await call.message.edit_text(
        new_text_storage.GETTiNG_CONNECTION_DATA,
        reply_markup=None
    )

    ok = await send_connection_data(call, client)

    if ok:
        await call.message.delete()


async def send_config_file(call, client: schemas.Client, data: str):

    filename = get_filename(client)

    async with tempfile.NamedTemporaryFile(
            mode="w+", delete=True
    ) as temp_file:
        await temp_file.write(data)
        await temp_file.flush()

        await call.message.answer_document(
            document=FSInputFile(temp_file.name, filename=filename),
        )


async def iphone_send_connection_data(call: CallbackQuery):

    caption = new_text_storage.IPHONE_CONNECTION_INSTRUCTION
    photos_dir = config.IPHONE_INSTRUCTION_PATH

    media_group = MediaGroupBuilder()
    photos = sorted(os.listdir(photos_dir))
    for ind, photo in enumerate(photos):
        media_data = {
            "media": FSInputFile(photos_dir / photo),
        }
        if ind == len(photos) - 1:
            media_data["caption"] = caption
            media_data["parse_mode"] = ParseMode.HTML
        media_group.add_photo(**media_data)

    await call.message.answer_media_group(
        media=media_group.build(),
        disable_web_page_preview=True,
    )


async def android_send_connection_data(call: CallbackQuery, client: schemas.Client, data: str):

    async with tempfile.NamedTemporaryFile(
        delete=True, suffix=".png", dir="./"
    ) as temp_file:
        qr = qrcode.make(data)
        temp_file_path = temp_file.name
        qr.save(temp_file_path)

        await call.message.answer_photo(
            photo=FSInputFile(temp_file_path),
            caption=new_text_storage.ANDROID_CONNECTION_INSTRUCTION,
            reply_markup=get_post_adding_device_keyboard(client, without_qr_alternative=True),
            parse_mode=ParseMode.HTML
        )

        await temp_file.flush()


async def send_connection_data(call: CallbackQuery, client: schemas.Client) -> bool:
    config_file_data = await get_config_file(
        user_id=call.from_user.id, client_id=client.id, call=call
    )

    if not config_file_data:
        return False

    try:
        if client.type == ClientTypeEnum.ANDROID:
            await android_send_connection_data(call, client, config_file_data)
            return True

        await send_config_file(call, client, config_file_data)

        if client.type == ClientTypeEnum.IPHONE:
            await iphone_send_connection_data(call)

        else:
            text = new_text_storage.WINDOWS_CONNECTION_INSTRUCTION if client.type == ClientTypeEnum.WINDOWS else new_text_storage.MACOS_CONNECTION_INSTRUCTION
            await call.message.answer(
                text=text,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )

        await call.message.answer(
            text=new_text_storage.IS_EVERYTHING_OK,
            reply_markup=get_post_adding_device_keyboard(client)
        )
        return True

    except Exception as e:
        logger.error("Error while sending phone connection data", exc_info=e)
        await call.message.edit_text(
            new_text_storage.SOMETHING_WENT_WRONG_ERROR_MSG,
            reply_markup=get_back_to_main_menu_keyboard(),
        )
        return False


@router.callback_query(
    PostAdditionDeviceFactory.filter(
        F.callback == ButtonsStorage.WITHOUT_QR.callback  # noqa
    )
)
async def handle_without_qr_query(call: CallbackQuery, callback_data: PostAdditionDeviceFactory):

    client = await get_client(call.from_user.id, callback_data.client_id, call)
    if not client:
        return

    config_file_data = await get_config_file(
        user_id=call.from_user.id, client_id=client.id, call=call
    )

    if not config_file_data:
        return False

    await call.message.edit_reply_markup(
        reply_markup=None
    )

    await send_config_file(call, client, config_file_data)

    await call.message.answer(
        text=new_text_storage.ANDROID_ALTERNATIVES,
        reply_markup=get_post_adding_device_keyboard(client),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )


@router.callback_query(
    PostAdditionDeviceFactory.filter()
)
async def handle_post_adding_device_query(call: CallbackQuery, callback_data: PostAdditionDeviceFactory):
    client = await get_client(call.from_user.id, callback_data.client_id, call)
    if not client:
        return

    msg_data = {
        "text": new_text_storage.TEXT_ME,
        "reply_markup": get_back_to_main_menu_keyboard(with_new_message=True),
        "parse_mode": ParseMode.HTML
    }

    if call.message.photo:
        await call.message.edit_reply_markup(reply_markup=None)
        await call.message.answer(**msg_data)
        return

    await call.message.edit_text(**msg_data)


@router.callback_query(
    DevicesCallbackFactory.filter(
        F.callback == ButtonsStorage.REACTIVATE_DEVICE.callback  # noqa
    )
)
async def handle_reactivate_device_query(
    call: CallbackQuery, callback_data: DevicesCallbackFactory
):
    client = await get_client(call.from_user.id, callback_data.id, call)
    if not client:
        return

    client_was_active = client.is_active

    if not client.is_active:

        await call.message.edit_text(
            text=new_text_storage.REACTIVATING_DEVICE
        )

        user = await get_user(call.from_user.id, call)
        if not user:
            return

        if not await check_user_balance_for_new_client(call, user, client):
            return

        client = await reactivate_client(call.from_user.id, client.id, call)
        if not client:
            return

        await call.bot.send_message(
            chat_id=call.from_user.id,
            text=new_text_storage.DEVICE_SUCCESSFULLY_REACTIVATED.format(client.price)
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
    servers = await get_servers(call)
    if servers is None:
        return

    if not servers:
        text = new_text_storage.NO_SERVERS_AVAILABLE
        keyboard = get_back_to_main_menu_keyboard()
    else:
        text = new_text_storage.CHOOSE_REGION
        keyboard = get_servers_keyboard(servers)

    await call.message.edit_text(
        text=text,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )


@router.callback_query(
    ServersCallbackFactory.filter(F.callback == ButtonsStorage.SERVER.callback)  # noqa
)
async def handle_choose_server_query(
        call: CallbackQuery, callback_data: ServersCallbackFactory
):
    server_id = callback_data.id
    server = await get_server(server_id, call)
    if not server:
        return

    if not server.has_available_ips:
        await call.answer(
            text=new_text_storage.SERVER_HAS_NO_FREE_IPS,
            show_alert=True
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
    user = await get_user(call.from_user.id, call)
    server = await get_server(callback_data.id, call)

    if not server or not user:
        return

    if not await check_user_balance_for_new_client(call, user, server):
        return

    choose_device_type_keyboard = get_choose_device_type_keyboard(server=server)
    await call.message.edit_text(
        text=new_text_storage.CHOOSE_DEVICE_TYPE,
        reply_markup=choose_device_type_keyboard,
    )


@router.callback_query(AddDeviceFactory.filter())
async def handle_add_device_query(call: CallbackQuery, callback_data: AddDeviceFactory):

    await call.message.edit_text(
        new_text_storage.CHECKING_ADDING_DATA
    )

    user = await get_user(call.from_user.id, call)
    server = await get_server(callback_data.id, call)

    if not user or not server or not await check_user_balance_for_new_client(call, user, server):
        await call.message.edit_text(
            new_text_storage.NOT_ENOUGH_MONEY_ERROR_MSG.format(user.balance),
            reply_markup=get_back_to_main_menu_keyboard(
                with_new_message=True
            )
        )
        return

    msg_to_edit = await call.message.answer(
        new_text_storage.ADDING_DEVICE,
    )

    client = await create_client(
        call.from_user.id, callback_data.id, callback_data.type, call
    )

    if not client:
        return

    await msg_to_edit.edit_text(
        new_text_storage.DEVICE_SUCCESSFULLY_ADDED,
    )

    await send_connection_data(call, client)


# EDITING DEVICES


@router.callback_query(
    DevicesCallbackFactory.filter(
        F.callback == ButtonsStorage.EDIT_DEVICE.callback  # noqa
    )
)
async def handle_specific_device_query(
        call: CallbackQuery, callback_data: DevicesCallbackFactory
):
    client = await get_client(call.from_user.id, callback_data.id, call)

    if not client:
        return

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
    old_client = await get_client(call.from_user.id, callback_data.id, call)
    if not old_client:
        return

    client = await patch_client(
        call.from_user.id, old_client.id, auto_renew=not old_client.auto_renew, call=call
    )

    if not client:
        return

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
    client = await get_client(call.from_user.id, callback_data.id, call)

    if not client:
        return

    await call.message.edit_text(
        text=new_text_storage.CHOOSE_DEVICE_TYPE,
        reply_markup=get_choose_device_type_keyboard(client=client),
    )


@router.callback_query(EditDeviceTypeCallbackFactory.filter())
async def handle_set_device_type_query(
        call: CallbackQuery, callback_data: EditDeviceTypeCallbackFactory
):
    client = await patch_client(
        call.from_user.id, callback_data.id, type=callback_data.type, call=call
    )

    if not client:
        return

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

    client = await patch_client(message.from_user.id, state_data["client_id"], name=message.text, call=message)
    if not client:
        return

    edited = await edit_safely(
        message.from_user.id,
        msg_to_edit.message_id,
        text=new_text_storage.DEVICE_SUCCESSFULLY_RENAMED,
        reply_markup=None
    )

    if not edited:
        await send_safely(
            message.from_user.id,
            text=new_text_storage.DEVICE_SUCCESSFULLY_RENAMED,
        )

    clients = await get_user_clients(message.from_user.id, message)

    if not clients:
        return

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
    client = await get_client(call.from_user.id, callback_data.id, call)

    if not client:
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
    await call.message.edit_text(
        new_text_storage.DELETING_DEVICE
    )
    deleted = await delete_client(call.from_user.id, callback_data.id, call)

    if not deleted:
        return

    await call.message.edit_text(
        new_text_storage.DEVICE_SUCCESSFULLY_DELETED,
        reply_markup=get_back_to_main_menu_keyboard(),
    )


# FINANCE


@router.callback_query(F.data == ButtonsStorage.FINANCE.callback)
async def handle_finance_callback_query(call: CallbackQuery):
    user = await get_user(call.from_user.id, call)

    if not user:
        return

    await call.message.edit_text(
        new_text_storage.BALANCE_INFO.format(user.balance),
        reply_markup=get_finance_callback(),
    )


@router.callback_query(F.data == ButtonsStorage.GET_TRANSACTIONS_HISTORY.callback)
async def handle_get_transactions_query(call: CallbackQuery):
    file_data = await get_transactions_history(call.from_user.id, call)
    if not file_data:
        return

    await delete_message_or_delete_markup(call.message)

    async with tempfile.NamedTemporaryFile(
            mode="w+", delete=True
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
        reply_markup=get_fill_up_balance_values_keyboard(from_admin),
    )


@router.callback_query(FillUpBalanceFactory.filter())
async def handle_fill_up_balance_factory_query(
        call: CallbackQuery, callback_data: FillUpBalanceFactory
):
    url = await gen_payment_url(call.from_user.id, callback_data.value, call)

    if not url:
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
        message.from_user.id, promo_code=message.text.strip(), call=msg_to_edit
    )

    if not applied:
        return

    await edit_safely(
        message.from_user.id,
        msg_to_edit.message_id,
        text=msg_to_edit.text,
        reply_markup=None,
    )

    await message.answer(
        text=new_text_storage.PROMO_CODE_SUCCESSFULLY_APPLIED.format(applied.value),
        reply_markup=get_back_to_main_menu_keyboard(),
    )


@router.callback_query(F.data == ButtonsStorage.INVITATION_LINK.callback)
async def handle_invitation_link_query(call: CallbackQuery):
    user_link = generate_invitation_link(call.from_user.id)
    await call.message.edit_text(
        new_text_storage.INVITATION_LINK_INFO_MSG.format(user_link),
        reply_markup=get_back_to_main_menu_keyboard(),
    )
