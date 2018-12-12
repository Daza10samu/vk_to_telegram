#! /usr/bin/python3

import os, configparser, telebot
from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api, datetime, threading

pwd = os.environ['HOME']+'/.config/vk_to_telegram'
config = configparser.ConfigParser()
config.read(pwd+'/config')
bot_token = config.get('General', 'bot_token')
send_ids = config.get('General', 'user_ids')
send_ids = [x.strip("[] '") for x in send_ids.split(',')]
bot = telebot.TeleBot(bot_token)

def bot_send(msg):
    for i in send_ids:
        bot.send_message(i, msg)

class LongPool(threading.Thread):

    def __init__(self, account):
        threading.Thread.__init__(self)
        self.paused = False
        self.token = account[0]
        self.chat_users = account[1]
        self.chats = account[2]

    def run(self):
        session = vk_api.VkApi(token=self.token)
        long_pooll = VkLongPoll(session)
        session = session.get_api()
        while 1:
            try:
                for i in long_pooll.listen():
                    if self.paused:
                        continue
                    if i.type == VkEventType.MESSAGE_NEW:
                        bot_send(str(session.messages.getById(message_ids=(i.message_id))))
            except Exception as exep:
                bot_send('Ohhh... there are some errors: '+str(exep))

    def stop(self):
        self.paused = True

    def resume(self):
        self.paused = False

@bot.message_handler(commands=['start'])
def handle_start(message):
    for i in threads:
        i.resume()
    for i in send_ids:
        bot.send_message(i, 'Bot have resumed')

@bot.message_handler(commands=['stop'])
def handle_stop(message):
    for i in threads:
        i.stop()
    for i in send_ids:
        bot.send_message(i, 'Bot have stoped')
@bot.message_handler(commands=['kill'])
def kill(message):
    for i in send_ids:
        bot.send_message(i, 'Bot have been killed')
    *proc, = os.popen('ps axu | grep resender')
    pid = proc[0].split()[1]
    os.system('kill '+pid)

accounts = [i.strip("[]' ") for i in config.get('General', 'vk_users').split(',')]
check_configs = []
for name in accounts:
    check_configs.append([config.get(name, 'token'), [int(i.strip("[] '")) for i in config.get(name, 'chat_users').split(',')], [int(i.strip("[] '")) for i in config.get(name, 'chats').split(',')]])

global threads
threads = []
for i in check_configs:
    threads.append(LongPool(i))
    threads[-1].start()

while 1:
    try:
        bot.polling(none_stop=True)
    except KeyboardInterrupt:
        exit()
    except Exception as exep:
        bot_send('Ohhh... there are some errors: '+str(exep))