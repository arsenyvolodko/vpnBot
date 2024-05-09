from aiogram.filters.callback_data import CallbackData


class DevicesCallbackFactory(CallbackData, prefix='devices_callback_factory'):
    callback: str
    device_num: int
