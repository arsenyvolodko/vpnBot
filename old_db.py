import datetime
import threading

import psycopg2
import time

from AlreadyAppointedQuestError import AlreadyAppointedQuestError, ConsistencyError
from config import *
from constants import MESSAGES_CONTAINER, QUEST_BY_BTN


class BotDB:

    def __init__(self):
        self.__try_to_connect()

    def __pool_connection(self):
        while True:
            try:
                # MESSAGES_CONTAINER.clear()
                self.cursor.execute("SELECT")
                print(f"the connection is stable: {datetime.datetime.now()}")
            except Exception as e:
                print("ERROR: No connection to DB.")
            time.sleep(60)

    def __try_to_connect(self):
        try:
            self.cursor = self.__connect()
            print("Successfully connected to DataBase")
            db_thread = threading.Thread(target=self.__pool_connection)
            db_thread.daemon = True  # Поток будет остановлен при завершении основного потока
            db_thread.start()
        except Exception as e:
            print(e)
            if "Unknown host" in str(e):
                print("Probably, there's no internet connection. Check wi-fi connection!")
            for i in range(5, 0, -1):
                print(f"Next request in {i} seconds")
                time.sleep(1)
            print('\n')
            self.__try_to_connect()

    def __connect(self):
        self.conn = psycopg2.connect(host=host_db,
                                     port=port_db,
                                     database=database,
                                     user=user_db,
                                     password=password_db,
                                     keepalives=1)
        return self.conn.cursor()

    def user_exists(self, tg_id):
        self.cursor.execute("SELECT id FROM points WHERE tg_id = %s", (tg_id,))
        result = self.cursor.fetchone()
        return bool(result)

    def user_exists_by_id(self, user_id):
        self.cursor.execute("SELECT id FROM points WHERE id = %s", (user_id,))
        result = self.cursor.fetchone()
        return bool(result)

    def get_user_id(self, tg_id):  # todo added NONE!!
        self.cursor.execute("SELECT id FROM points WHERE tg_id = %s", (tg_id,))
        result = self.cursor.fetchone()
        return result[0] if bool(result) else None

    def get_tg_id_by_id(self, user_id):  # todo added NONE!!
        self.cursor.execute("SELECT tg_id FROM points WHERE id = %s", (user_id,))
        result = self.cursor.fetchone()
        return result[0] if bool(result) else None

    def add_user(self, tg_id, name='', gmail=''):
        self.cursor.execute("INSERT INTO points (tg_id, name, gmail) VALUES (%s, %s, %s)", (tg_id, name, gmail))
        self.conn.commit()
        return True

    def add_record(self, user_id, val, location, when: str, by_user: int):
        self.cursor.execute(
            "INSERT INTO records (users_id, value, location, time, by_user) VALUES (%s, %s, %s, %s, %s)", (
                user_id,
                val,
                location,
                when,
                by_user,
            ))
        return self.conn.commit()

    def update_total_scores(self, user_id, delta):
        self.cursor.execute("UPDATE points SET points_sum = points_sum + %s WHERE id = %s", (delta, user_id))
        return self.conn.commit()

    def get_scores_by_user_id(self, user_id):
        self.cursor.execute("SELECT points_sum FROM points WHERE id = %s", (user_id,))
        result = self.cursor.fetchone()
        return result[0] if bool(result) else 0

    def mark_as_admin(self, tg_id):
        self.cursor.execute("UPDATE points SET admin = 1 WHERE tg_id = %s",
                            (tg_id,))
        return self.conn.commit()

    def check_if_admin(self, tg_id):
        if not self.user_exists(tg_id):
            return False
        self.cursor.execute("SELECT admin FROM points WHERE tg_id = %s", (tg_id,))
        result = self.cursor.fetchone()
        return bool(result[0]) if result else False

    def update_admin_query(self, tg_id,
                           query_val):  # todo added return or and false
        self.cursor.execute("UPDATE points SET admin_query = %s WHERE tg_id = %s",
                            (
                                query_val,
                                tg_id,
                            ))
        self.conn.commit()

    def get_admin_query(self, tg_id):  # todo added None
        self.cursor.execute("SELECT admin_query FROM points WHERE tg_id = %s",
                            (tg_id,))
        result = self.cursor.fetchone()
        return result[0] if bool(result) else None

    def update_gmail(self, tg_id, new_gmail):
        self.cursor.execute("UPDATE points SET gmail = %s WHERE tg_id = %s",
                            (new_gmail, tg_id))
        self.conn.commit()

    def get_name_by_user_id(self, user_id):  # todo added None
        self.cursor.execute("SELECT name FROM points WHERE id = %s", (user_id,))
        result = self.cursor.fetchone()
        return result[0] if bool(result) else None

    def get_name_by_tg_id(self, tg_id):  # todo added None
        self.cursor.execute("SELECT name FROM points WHERE tg_id = %s", (tg_id,))
        result = self.cursor.fetchone()
        return result[0] if bool(result) else None

    def get_records(self, user_id):  # todo added None
        self.cursor.execute("SELECT value, location, time FROM records WHERE users_id = %s", (user_id,))
        result = self.cursor.fetchall()
        return result if bool(result) else None

    def get_all_id_users(self):
        self.cursor.execute("SELECT tg_id FROM points WHERE tg_id > 0")
        result = self.cursor.fetchall()
        return result if bool(result) else None

    def get_user_scores_on_location_by(self, user_id, location: str):
        self.cursor.execute("SELECT value FROM records WHERE users_id = %s AND location = %s", (user_id, location))
        result = self.cursor.fetchall()
        return result if bool(result) else []

    def check_quest_appointment(self, user_id, quest):
        table = quest.table_name
        self.cursor.execute(f"SELECT user_id FROM {table} WHERE user_id = %s", (user_id,))
        result = self.cursor.fetchone()
        return bool(result)

    def check_quest_appointment_in_all_tables(self, user_id):
        quests = QUEST_BY_BTN.values()
        for quest in quests:
            if self.check_quest_appointment(user_id, quest):
                return True
        return False

    def get_group_number_by_user_id(self, user_id, quest):
        if quest != 'ANY':
            self.cursor.execute(f"SELECT group_num FROM {quest.table_name} WHERE user_id = %s", (user_id,))
            result = self.cursor.fetchone()
            if bool(result):
                return result[0], quest
            else:
                raise ConsistencyError()
        else:
            quests = QUEST_BY_BTN.values()
            for quest in quests:
                if self.check_quest_appointment(user_id, quest):
                    return self.get_group_number_by_user_id(user_id, quest)
            raise ConsistencyError()

    # return False if incorrect result else group number
    def get_new_group_number(self, quest):
        self.cursor.execute(f"SELECT COUNT(*) FROM {quest.table_name}")
        count = self.cursor.fetchone()[0]  # todo what if zero records
        group_num = count // 10 + 1
        if group_num > quest.group_number:
            raise ConsistencyError()
        return group_num

    def add_quest_appointment(self, user_id, name, quest):
        if self.check_quest_appointment(user_id, quest):
            raise AlreadyAppointedQuestError(self.get_group_number_by_user_id(user_id, quest), quest)
        group_num = self.get_new_group_number(quest)
        # self.cursor.execute("INSERT INTO points (tg_id, name, gmail) VALUES (%s, %s, %s)", (tg_id, name, gmail))
        self.cursor.execute(f"INSERT INTO {quest.table_name} (user_id, name, group_num) VALUES (%s, %s, %s)", (user_id, name, group_num))
        self.conn.commit()
        return group_num

    def deny_quest_appointment(self, user_id):
        quest_table = 0
        quests = QUEST_BY_BTN.values()
        for quest in quests:
            if self.check_quest_appointment(user_id, quest):
                quest_table = quest.table_name
                break
        if quest_table:
            self.cursor.execute(f"DELETE FROM {quest_table} WHERE user_id = %s", (user_id,))
            self.conn.commit()
        return True

    def get_free_places_for_quests(self):
        quests = QUEST_BY_BTN.values()
        result = [0] * len(quests)
        for quest in quests:
            tablee = quest.table_name
            self.cursor.execute(f"SELECT COUNT(*) FROM {tablee}")
            count = self.cursor.fetchall()[0]
            count = count[0] if len(count) else 0
            # print(count)
            result[int(tablee[-1]) - 1] = quest.group_number * 10 - count
        return tuple(result)

    def close(self):
        """Закрываем соединение с БД"""
        self.conn.close()
