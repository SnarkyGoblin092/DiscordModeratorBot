from flask import Flask
from threading import Thread

app = Flask('')


# prints message to the webserver
@app.route('/')
def home():
  return "Hello, I am alive!"


# runs webserver
def run():
  app.run(host='0.0.0.0', port=8080)


#starts the webserver on a thread
def keep_alive():
  t = Thread(target=run)
  t.start()