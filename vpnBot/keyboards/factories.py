from aiogram.filters.callback_data import CallbackData


class DevicesCallbackFactory(CallbackData, prefix="devices_callback_factory"):
    callback: str
    device_num: int


class FillUpBalanceFactory(CallbackData, prefix="fill_up_balance_factory"):
    value: int
