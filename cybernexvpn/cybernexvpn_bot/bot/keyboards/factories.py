from aiogram.filters.callback_data import CallbackData

from cybernexvpn.cybernexvpn_client.enums import ClientTypeEnum


class DevicesCallbackFactory(CallbackData, prefix="dcf"):
    callback: str
    id: int


class EditDeviceTypeCallbackFactory(
    CallbackData, prefix="edtcf"
):
    id: int
    type: ClientTypeEnum


class ServersCallbackFactory(CallbackData, prefix="scf"):
    callback: str
    id: int


class FillUpBalanceFactory(CallbackData, prefix="fubf"):
    value: int


class AddDeviceFactory(CallbackData, prefix="adf"):
    id: int  # server id
    type: ClientTypeEnum | None = None


class PostAdditionDeviceFactory(CallbackData, prefix="padf"):
    client_id: int
    callback: str
