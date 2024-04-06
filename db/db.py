import psycopg2

from classes_util.Exceptions.NoFreeIPsError import NoFreeIPsError
from classes_util.Client import Client
from classes_util.Exceptions.NoSuchClientExistsError import NoSuchClientExistsError
from classes_util.Ips import Ips
from classes_util.Keys import Keys
import config


class BotDB:

    def __init__(self):
        self.conn = self.__connect()

    @staticmethod
    def __connect():
        conn = psycopg2.connect(
            host=config.DB_HOST,
            port=5432,
            database=config.DB_NAME,
            user=config.DB_USERNAME,
            password=config.DB_PASSWORD
        )
        return conn

    # * balance table
    def user_exists(self, user_id: int):
        with self.conn, self.conn.cursor() as cursor:
            cursor.execute("SELECT user_id FROM balance_table WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
        return bool(result)

    def update_balance(self, user_id: int, new_balance: int):

        if new_balance < 0:
            return False
            # raise NotEnoughMoneyError(f"Incorrect balance value: {new_balance}")

        with self.conn, self.conn.cursor() as cursor:
            cursor.execute("UPDATE balance_table SET balance = %s WHERE user_id = %s", (new_balance, user_id))
            self.conn.commit()
        return True

    def get_balance(self, user_id: int):
        with self.conn, self.conn.cursor() as cursor:
            cursor.execute("SELECT balance FROM balance_table WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
        return int(result[0])

    def set_promo_flag(self, user_id: int, value: int):
        with self.conn, self.conn.cursor() as cursor:
            cursor.execute("UPDATE balance_table SET promo_flag = %s WHERE user_id = %s",
                           (value, user_id))
            self.conn.commit()

    def get_promo_flag(self, user_id: int):
        with self.conn, self.conn.cursor() as cursor:
            cursor.execute("SELECT promo_flag FROM balance_table WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            if result and len(result):
                return bool(result[0])
        return False

    # promocodes

    def get_used_promocodes(self, user_id: int):
        with self.conn, self.conn.cursor() as cursor:
            cursor.execute("SELECT promo FROM promocodes WHERE user_id = %s", (user_id,))
            result = list(map(lambda x: x[0], cursor.fetchall()))
        return result

    def add_used_promocode(self, user_id: int, promocode: str):
        with self.conn, self.conn.cursor() as cursor:
            cursor.execute("INSERT INTO promocodes (user_id, promo) VALUES (%s, %s)", (user_id, promocode))
            self.conn.commit()
            return True

    # * clients table

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
            cursor.execute("DELETE FROM clients WHERE user_id = %s and device_num = %s", (user_id, device_num,))
            self.conn.commit()
            return True

    def get_user_devices(self, user_id: int):
        with self.conn, self.conn.cursor() as cursor:
            cursor.execute("SELECT device_num, active FROM clients WHERE user_id = %s ORDER BY device_num", (user_id,))
            result = cursor.fetchall()
        return result

    def get_client(self, user_id: int, device_num: int):  # throws NoSuchClientExistsError
        with self.conn, self.conn.cursor() as cursor:
            cursor.execute(
                "SELECT ipv4, private_key, preshared_key, end_date FROM clients WHERE user_id = %s and device_num = %s",
                (user_id, device_num))
            result = cursor.fetchone()
            if not result:
                raise NoSuchClientExistsError()
            ips = Ips(ipv4=result[0])
            keys = Keys(result[1], None, result[2])
            return Client(user_id, device_num, ips, keys, result[3])

    def update_client_end_date(self, user_id: int, device_num: int, new_date):
        with self.conn, self.conn.cursor() as cursor:
            cursor.execute("UPDATE clients SET end_date = %s WHERE user_id = %s and device_num = %s",
                           (new_date, user_id, device_num))
            self.conn.commit()

    def get_client_end_date(self, user_id: int, device_num: int):
        with self.conn, self.conn.cursor() as cursor:
            cursor.execute("SELECT end_date FROM clients WHERE user_id = %s and device_num = %s",
                           (user_id, device_num))
            result = cursor.fetchone()
        return result[0]

    def get_clients_to_pay(self, date: str):
        return self.__get_clients_to_pay_or_delete(date, 1, True)

    def get_clients_to_delete(self, date: str):
        return self.__get_clients_to_pay_or_delete(date, 0, False)

    def __get_clients_to_pay_or_delete(self, date: str, active: int, strict: bool):
        with self.conn, self.conn.cursor() as cursor:
            if strict:
                cursor.execute(f"SELECT user_id, device_num FROM clients WHERE end_date = %s and active = %s",
                               (date, active))
                result = cursor.fetchall()
            else:
                cursor.execute(f"SELECT user_id, device_num FROM clients WHERE end_date <= %s and active = %s",
                               (date, active))
                result = cursor.fetchall()
        return result

    def get_client_ip(self, user_id: int, device_num: int):
        with self.conn, self.conn.cursor() as cursor:
            cursor.execute(f"SELECT ipv4 FROM clients WHERE user_id = %s and device_num = %s", (user_id, device_num))
            result = cursor.fetchone()
        return result[0]

    def change_client_activity(self, user_id: int, device_num: int, new_active_value: int):
        with self.conn, self.conn.cursor() as cursor:
            cursor.execute("UPDATE clients SET active = %s WHERE user_id = %s and device_num = %s",
                           (new_active_value, user_id, device_num))
            self.conn.commit()

    def check_if_active(self, user_id: int, device_num: int):
        with self.conn, self.conn.cursor() as cursor:
            cursor.execute(f"SELECT active FROM clients WHERE user_id = %s and device_num = %s", (user_id, device_num))
            result = cursor.fetchone()
        return result[0]

    # * free ips table

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
        if not self.ip_exists_in_clients(ips):
            if not self.ip_exists_in_free_ips(ips):
                with self.conn, self.conn.cursor() as cursor:
                    cursor.execute("INSERT INTO free_ips (ipv4) VALUES (%s)", (ips.get_ipv4(True),))
                    self.conn.commit()
                    return True
        else:
            return False

    def get_next_free_ips(self):
        with self.conn, self.conn.cursor() as cursor:
            cursor.execute("SELECT ipv4 FROM free_ips WHERE id = (SELECT MIN(id) FROM free_ips)")
            row = cursor.fetchone()
            if row:
                ips = Ips(row[0])
                cursor.execute("DELETE FROM free_ips WHERE ipv4 = %s", (ips.get_ipv4(True),))
                self.conn.commit()
            else:
                raise NoFreeIPsError("No free Ips available")
        return ips

    # * transactions table

    def add_user(self, username: int, user_id: int, initial_balance: int):
        if self.user_exists(user_id):
            return
        if username is None:
            username = "unknown"
        with self.conn, self.conn.cursor() as cursor:
            cursor.execute("INSERT INTO balance_table (user_id, username, balance) VALUES (%s, %s, %s)",
                           (user_id, username, initial_balance))
            self.conn.commit()

    def add_transaction(self, user_id: int, operation_type: int, value: int, operation_time: str, comment: str = ''):
        with self.conn, self.conn.cursor() as cursor:
            cursor.execute("INSERT INTO transactions "
                           "(user_id, operation_type, value, operation_time, comment) "
                           "VALUES (%s, %s, %s, %s, %s)",
                           (user_id, operation_type, value, operation_time, comment))
            self.conn.commit()

        return True

    def get_transactions(self, user_id: int):
        with self.conn, self.conn.cursor() as cursor:
            cursor.execute("SELECT operation_type, value, operation_time, comment "
                           "FROM transactions WHERE user_id = %s ORDER BY operation_time", (user_id,))
            result = cursor.fetchall()
        return result

    def update_transaction_time(self, user_id: int, old_operation_time: str, new_operation_time: str):
        with self.conn, self.conn.cursor() as cursor:
            cursor.execute("UPDATE transactions SET operation_time = %s WHERE user_id = %s and operation_time = %s",
                           (new_operation_time, user_id, old_operation_time))
            self.conn.commit()

    def get_all_users(self):
        with self.conn, self.conn.cursor() as cursor:
            cursor.execute("SELECT user_id FROM balance_table")
            result = cursor.fetchall()
        return list(map(lambda x: int(x[0]), result))

    def close(self):
        self.conn.close()
