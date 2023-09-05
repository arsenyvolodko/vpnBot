from flask import Flask, request
from threading import Thread
import time

app = Flask('')


def db_request():
  time.sleep(120)


@app.route('/')
def home():
  return "I'm alive"


def run():
  app.run(host='0.0.0.0', port=80)


def keep_alive():
  t = Thread(target=run)
  t.start()
