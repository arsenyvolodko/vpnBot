from vpnBot.bot.main import bot
from vpnBot.config import MY_TG_ID
from vpnBot.db import db_manager
from vpnBot.db.tables import User
from vpnBot.utils.bot_funcs import send_message_safety

if __name__ == "__main__":
    users = db_manager.get_records(User)
    cnt, total = 0, len(users)
    for user in users:
        if user.id != MY_TG_ID:
            continue
        send_message_safety(
            bot, user.id, text=""
        )
        cnt += 1
    print(f"successfully sent: {cnt}/{total}.")
