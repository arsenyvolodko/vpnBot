from aiogram.filters.callback_data import CallbackData

from cybernexvpn.cybernexvpn_client.enums import ClientTypeEnum


class DevicesCallbackFactory(CallbackData, prefix="devices_callback_factory"):
    callback: str
    id: int


class EditDeviceTypeCallbackFactory(
    CallbackData, prefix="edit_device_type_callback_factory"
):
    id: int
    type: ClientTypeEnum


class ServersCallbackFactory(CallbackData, prefix="servers_callback_factory"):
    callback: str
    id: int


class FillUpBalanceFactory(CallbackData, prefix="fill_up_balance_factory"):
    value: int


class AddDeviceFactory(CallbackData, prefix="add_device_factory"):
    id: int  # server id
    type: ClientTypeEnum | None = None
