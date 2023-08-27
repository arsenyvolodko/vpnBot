import datetime
import threading

import psycopg2
import time

from system.config import *


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


    def close(self):
        self.conn.close()
