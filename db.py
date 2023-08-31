import datetime
import threading

import psycopg2
import time

from Client import Client, NoSuchClientExistsError
from Exceptions.NotEnoughMoneyError import NotEnoughMoneyError
from Ips import Ips
from Keys import Keys
from constants import PRICE
from system.config import *


class BotDB:

    def __init__(self):
        self.conn = self.__connect()
        # self.__try_to_connect()

    # def __pool_connection(self):
    #     while True:
    #         try:
    #             # MESSAGES_CONTAINER.clear()
    #             cursor.execute("SELECT")
    #             print(f"the connection is stable: {datetime.datetime.now()}")
    #         except Exception as e:
    #             print("ERROR: No connection to DB.")
    #         time.sleep(60)

    # def __try_to_connect(self):
    #     try:
    #         cursor = self.__connect()
    #         print("Successfully connected to DataBase")
    #         db_thread = threading.Thread(target=self.__pool_connection)
    #         db_thread.daemon = True  # Поток будет остановлен при завершении основного потока
    #         db_thread.start()
    #     except Exception as e:
    #         print(e)
    #         if "Unknown host" in str(e):
    #             print("Probably, there's no internet connection. Check wi-fi connection!")
    #         for i in range(5, 0, -1):
    #             print(f"Next request in {i} seconds")
    #             time.sleep(1)
    #         print('\n')
    #         self.__try_to_connect()

    def __connect(self):
        conn = psycopg2.connect(host=host_db,
                                     port=port_db,
                                     database=database,
                                     user=user_db,
                                     password=password_db,
                                     keepalives=1)
        return conn


    def user_exists(self, user_id: int):
        with self.conn, self.conn.cursor() as cursor:
            cursor.execute("SELECT id FROM balance_table WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            print(f'res: {result}')
        print(bool(result))
        return bool(result)


    def add_client_to_db(self, client: Client):
        with self.conn, self.conn.cursor() as cursor:
            ipv4 = client.ips.get_ipv4(True)
            private_key, preshared_key = client.keys.private_key, client.keys.preshared_key
            cursor.execute("INSERT INTO clients "
                                "(user_id, device_num, ipv4, private_key, preshared_key, active, end_date) "
                                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                                (client.user_id, client.device_num, ipv4, private_key, preshared_key, 1, client.end_date))
            self.conn.commit()
        return True


    def remove_client_from_db(self, user_id: int, device_num: int):
        with self.conn, self.conn.cursor() as cursor:
            cursor.execute("DELETE FROM clients WHERE user_id = %s and device_num = %s", (user_id, device_num, ))
            # todo должен ли я писать self.conn.commit() при удалении строки из бд ??
            return True

    def get_user_devices(self, user_id: int):
        with self.conn, self.conn.cursor() as cursor:
            cursor.execute("SELECT device_num FROM clients WHERE user_id = %s ORDER BY device_num", (user_id,))
            result = cursor.fetchall()
        return list(map(lambda x: int(x[0]), result))


    def get_client(self, user_id: int, device_num: int):  # throws NoSuchClientExistsError
        with self.conn, self.conn.cursor() as cursor:
            cursor.execute("SELECT ipv4, private_key, preshared_key, end_date FROM clients WHERE user_id = %s and device_num = %s", (user_id, device_num))
            result = cursor.fetchone()
            if not result:
                raise NoSuchClientExistsError()
            ips = Ips(ipv4=result[0])
            keys = Keys(result[1], None, result[2])
            return Client(user_id, device_num, ips, keys, result[3])


    def add_transaction(self, user_id: int, operation_type: int, value: float, operation_time: str):
        balance = self.get_balance(user_id)
        try:
            if operation_type == 1:
                self.update_balance(user_id, balance + value)
            else:
                if balance < value:
                    raise NotEnoughMoneyError(f"Not enough money to write off. value: {value}, balance: {balance}.")
                else:
                    self.update_balance(user_id, balance - value)

        except AssertionError as e:
            raise NotEnoughMoneyError(e)

        with self.conn, self.conn.cursor() as cursor:
            cursor.execute("INSERT INTO transactions "
                           "(user_id, operation_type, value, operation_time) "
                           "VALUES (%s, %s, %s, %s)",
                           (user_id, operation_type, value, operation_time))
            self.conn.commit()

        return True

    '''
    "INSERT INTO clients "
                                "(user_id, device_num, ipv4, private_key, preshared_key, active, end_date) "
                                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                                (client.user_id, client.device_num, ipv4, private_key, preshared_key, 1, client.end_date))'''


    # def add_user(self, user_id: int):
    #     with self.conn, self.conn.cursor() as cursor:
    #         cursor.execute("INSERT into balance_table (user_id, balance) VALUES (%s, %s)", (user_id, PRICE))
    #         self.conn.commit()

    def update_balance(self, user_id: int, new_balance: float):
        if new_balance < 0:
            raise AssertionError(f"Incorrect balance value: {new_balance}")

        if not self.user_exists(user_id):
            with self.conn, self.conn.cursor() as cursor:
                cursor.execute("INSERT into balance_table (user_id, balance) VALUES (%s, %s)", (user_id, PRICE))
                self.conn.commit()
            return

        with self.conn, self.conn.cursor() as cursor:
            cursor.execute("UPDATE balance_table SET balance = %s WHERE user_id = %s", (new_balance, user_id))
            self.conn.commit()




    def get_balance(self, user_id: int):
        with self.conn, self.conn.cursor() as cursor:
            cursor.execute("SELECT balance FROM balance_table WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
        return float(result[0])


    ### FREE_IP DATABASE

    def ip_exists_in_free_ips(self, ips: Ips):
        with self.conn, self.conn.cursor() as cursor:
            cursor.execute("SELECT id FROM free_ips WHERE ipv4 = %s", (ips.get_ipv4(True),))
            result = cursor.fetchone()
        return bool(result)

    def ip_exists_in_clients(self, ips: Ips):
        with self.conn, self.conn.cursor() as cursor:
            cursor.execute("SELECT id FROM clients WHERE ipv4 = %s", (ips.get_ipv4(True),))
            result = cursor.fetchone()
        return bool(result)

    def add_free_ips(self, ips: Ips):
        with self.conn, self.conn.cursor() as cursor:
            if not self.ip_exists_in_clients(ips) and not self.ip_exists_in_free_ips(ips):
                cursor.execute("INSERT INTO free_ips (ipv4) VALUES (%s)", (ips.get_ipv4(True),))
                self.conn.commit()
                return True
            else:
                return False

    def get_next_free_ips(self):  # todo add no more free ips error
        with self.conn, self.conn.cursor() as cursor:
            cursor.execute("SELECT ipv4 FROM free_ips WHERE id = (SELECT MIN(id) FROM free_ips)")
            row = cursor.fetchone()
            if row:
                ips = Ips(row[0])
            #     cursor.execute("DELETE FROM free_ips WHERE ipv4 = %s", (ips.get_ipv4(True),))
            # todo должен ли я писать self.conn.commit() при удалении строки из бд ??
        return ips


    def close(self):
        self.conn.close()
