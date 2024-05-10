from aiogram.filters.callback_data import CallbackData


class FillUpBalanceFactory(CallbackData, prefix="fill_up_balance_factory"):
    callback: str
    value: int
